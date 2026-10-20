import logging

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from celery import shared_task
from moz.l10n.message import message_from_json

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.db.models import CharField, Q, Value as V
from django.db.models.functions import Concat
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    TranslatedResource,
    Translation,
    User,
)
from pontoon.base.tasks import PontoonTask
from pontoon.base.user_utils import get_pretranslation_authors
from pontoon.checks.libraries import run_checks
from pontoon.translations.utils import parse_source_string_to_json

from .pretranslate import get_pretranslation


if TYPE_CHECKING:
    from pontoon.sync.upload import PretranslationDecision, ReviewState


log = logging.getLogger(__name__)


@dataclass
class StagedPretranslation:
    """
    A pretranslation decided for one entity, not yet written:
    - `decision`: what to do with the entity's translations
    - `bot`: the pretranslation author (TM or Google Translate) that produced it,
      recorded as rejecting the translation it replaces.
    - `new`: the translation to create, if no existing one matches
    - `read_state`: the review state of the entity's translations as read when the
      decision was made, keyed by translation id, to detect concurrent changes
    """

    entity: Entity
    decision: "PretranslationDecision"
    bot: User
    read_state: "dict[int, ReviewState]"
    new: Translation | None = None

    @property
    def translation(self) -> Translation:
        """The row holding the pretranslation, whether created or matched."""
        return self.new or self.decision.match


def write_pretranslations(
    locale: Locale, staged: list[StagedPretranslation]
) -> list[StagedPretranslation]:
    """
    Write the staged pretranslations of `locale` to the database, along with their
    action log entries, and mark them as changed for sync. Return those written.

    A string whose translations changed after they were read, by a review, a new
    translation or a deletion, is left out: its pretranslation was decided on a state
    that no longer exists.

    Must run inside a transaction.
    """
    # Imported here: pontoon.sync.core imports this module.
    from pontoon.checks.models import Error, Warning
    from pontoon.sync.upload import (
        ReviewState,
        lock_import_target,
        reject_translations,
    )

    entity_ids = [change.entity.pk for change in staged]

    # Wait for uploads targeting the same strings to commit, so that the translations
    # they add are visible to the re-read below.
    lock_import_target(entity_ids)

    # Re-read all unrejected translations of the staged strings, not only those read
    # before, so that translations added since then are noticed as well. Locking them
    # waits for concurrent transactions on these rows to commit.
    current: dict[int, dict[int, ReviewState]] = defaultdict(dict)
    for entity_id, pk, *state in (
        Translation.objects.select_for_update()
        .filter(entity_id__in=entity_ids, locale=locale, rejected=False)
        .order_by("pk")
        .values_list("entity_id", "pk", *ReviewState._fields)
    ):
        current[entity_id][pk] = ReviewState(*state)

    written: list[StagedPretranslation] = []
    for change in staged:
        if current.get(change.entity.pk, {}) == change.read_state:
            written.append(change)
        else:
            log.info(
                f"Pretranslation skipped for entity {change.entity.pk} in {locale.code}: "
                "its translations changed while pretranslating"
            )
    if not written:
        return []

    now = timezone.now()
    reject_ids_by_bot: dict[User, list[int]] = defaultdict(list)
    for change in written:
        reject_ids_by_bot[change.bot].extend(change.decision.reject_ids)
    deactivate_ids = [pk for change in written for pk in change.decision.deactivate_ids]
    matched = [
        change.decision.match for change in written if change.decision.match is not None
    ]
    created = [change.new for change in written if change.new is not None]

    # Rejections and deactivations must be written before translations are activated,
    # to keep a single active translation per entity and locale.
    # Each rejection is recorded as done by the bot whose pretranslation replaces it.
    actions: list[ActionLog] = []
    for bot, ids in reject_ids_by_bot.items():
        actions.extend(reject_translations(ids, now=now, user=bot))
    if deactivate_ids:
        Translation.objects.filter(pk__in=deactivate_ids).update(active=False)
    if matched:
        Translation.objects.bulk_update(matched, ["active", "fuzzy", "pretranslated"])
    if created:
        Translation.objects.bulk_create(created)

    actions.extend(
        ActionLog(
            action_type=ActionLog.ActionType.TRANSLATION_CREATED,
            created_at=now,
            performed_by=tx.user,
            translation=tx,
        )
        for tx in created
    )
    if actions:
        ActionLog.objects.bulk_create(actions)

    # Only pretranslations passing all checks are staged, so there are no failed
    # checks to store. Those stored for a matched translation date from when it was
    # written, and no longer apply.
    matched_ids = [tx.pk for tx in matched]
    if matched_ids:
        Warning.objects.filter(translation_id__in=matched_ids).delete()
        Error.objects.filter(translation_id__in=matched_ids).delete()

    Translation.objects.filter(
        pk__in=[change.translation.pk for change in written]
    ).bulk_mark_changed()
    return written


def update_pretranslated_resources(
    locale: Locale, written: list[StagedPretranslation]
) -> None:
    """
    Update the stats and the latest translation of the resources of `locale` with
    written pretranslations.
    """
    # The newest written translation of each resource. A matched translation may be
    # older than the pretranslations created in the same resource.
    latest: dict[int, Translation] = {}
    for change in written:
        tx = change.translation
        previous = latest.get(change.entity.resource_id)
        if previous is None or tx.date > previous.date:
            latest[change.entity.resource_id] = tx

    TranslatedResource.objects.filter(
        locale=locale, resource_id__in=latest
    ).calculate_stats()
    for tx in latest.values():
        tx.update_latest_translation()


def pretranslate(project: Project, paths: set[str] | None):
    """
    Pretranslate the strings of a project with TheAlgorithm (bug 1552796),
    following the same rules as the pretranslation upload API.

    Strings with an approved translation or an existing pretranslation are skipped,
    as are strings whose pretranslation by a bot was previously rejected.
    A suggestion or fuzzy translation matching the pretranslation becomes the active
    pretranslation, keeping its author; a different fuzzy translation is rejected,
    and other suggestions are kept. Pretranslations that still fail checks after a
    retry are not stored.

    Each locale is written in its own transaction. A string whose translations
    changed while pretranslating is left out.

    :arg project: The project to be pretranslated
    :arg paths: Paths of the project resources to be pretranslated,
      or None to pretranslate all resources.

    :returns: None
    """
    from pontoon.sync.upload import (
        decide_pretranslation,
        read_state,
        translations_by_entity,
    )

    if not project.pretranslation_enabled:
        log.info(f"Pretranslation not enabled for project {project.name}")
        return

    locales = project.locales.filter(
        project_locale__pretranslation_enabled=True,
        project_locale__readonly=False,
    )

    if not locales:
        log.info(
            f"Pretranslation not enabled for any locale within project {project.name}"
        )
        return

    log.info(f"Fetching pretranslations for project {project.name} started")

    entities = Entity.objects.filter(resource__project=project, obsolete=False)
    if paths:
        entities = entities.filter(resource__path__in=paths)
    entities = entities.prefetch_related("resource")

    # Fetch all available locale-resource pairs (TranslatedResource objects)
    tr_pairs = (
        TranslatedResource.objects.filter(
            resource__project=project,
            locale__in=locales,
        )
        .annotate(
            locale_resource=Concat(
                "locale_id", V("-"), "resource_id", output_field=CharField()
            )
        )
        .values_list("locale_resource", flat=True)
        .distinct()
    )

    # Fetch all locale-entity pairs not to pretranslate: with an approved translation,
    # an existing pretranslation, or a pretranslation rejected from a bot.
    pt_authors = get_pretranslation_authors()
    skipped_entities = set(
        Translation.objects.filter(locale__in=locales, entity__in=entities)
        .filter(
            Q(rejected=False, approved=True)
            | Q(rejected=False, pretranslated=True)
            | Q(rejected=True, user__in=pt_authors.values())
        )
        .annotate(
            locale_entity=Concat(
                "locale_id", V("-"), "entity_id", output_field=CharField()
            )
        )
        .values_list("locale_entity", flat=True)
        .distinct()
    )

    for locale in locales:
        log.info(f"Fetching pretranslations for locale {locale.code} started")

        candidates = [
            entity
            for entity in entities
            if f"{locale.id}-{entity.id}" not in skipped_entities
            and f"{locale.id}-{entity.resource.id}" in tr_pairs
        ]

        rows_by_entity = translations_by_entity(
            locale, [entity.pk for entity in candidates], include_rejected=False
        )

        staged: list[StagedPretranslation] = []

        for entity in candidates:
            # Check again: a translation may have been approved or
            # pretranslated since the skipped entities were fetched.
            rows = rows_by_entity.get(entity.pk, [])
            if any(tx.approved or tx.pretranslated for tx in rows):
                continue

            entity_desc = (
                f"entity {entity.pk} ({entity.resource.path}) in {locale.code}"
            )

            try:
                pretranslation = get_pretranslation(entity, locale)
            except ValueError as e:
                log.info(f"Pretranslation error for {entity_desc}: {e!r}")
                continue

            failed_checks = run_checks(
                entity,
                locale.code,
                pretranslation[0],
                use_tt_checks=False,
            )

            if failed_checks:
                try:
                    pretranslation = get_pretranslation(
                        entity, locale, preserve_placeables=True
                    )
                except ValueError as e:
                    log.info(f"Pretranslation error for {entity_desc}: {e!r}")
                    continue
                # Check the second attempt as well: preserving placeables doesn't
                # fix every failure, and a pretranslation failing checks is not stored.
                failed_checks = run_checks(
                    entity,
                    locale.code,
                    pretranslation[0],
                    use_tt_checks=False,
                )
                if failed_checks:
                    log.info(
                        f"Pretranslation failed checks for {entity_desc}: {failed_checks!r}"
                    )
                    continue

            string, author_key = pretranslation
            try:
                _, value, properties = parse_source_string_to_json(
                    entity.resource.format, string, locale.plural_catchall
                )
            except ValueError as e:
                log.error(
                    f"Unparsable pretranslation for {entity_desc}: {e!r}: {string!r}"
                )
                continue

            decision = decide_pretranslation(
                rows,
                message_from_json(value),
                (
                    {key: message_from_json(prop) for key, prop in properties.items()}
                    if properties
                    else None
                ),
            )

            if decision.outcome != "change":
                continue

            change = StagedPretranslation(
                entity=entity,
                decision=decision,
                bot=pt_authors[author_key],
                read_state=read_state(rows),
            )
            if decision.match is None:
                change.new = Translation(
                    entity=entity,
                    locale=locale,
                    string=string,
                    value=value,
                    properties=properties,
                    user=change.bot,
                    approved=False,
                    pretranslated=True,
                    active=True,
                )
            else:
                decision.match.pretranslated = True
                decision.match.fuzzy = False
                decision.match.active = True
            staged.append(change)

        if not staged:
            log.info(
                f"Fetching pretranslations for locale {locale.code} done: No pretranslation fetched"
            )
            continue

        try:
            with transaction.atomic():
                written = write_pretranslations(locale, staged)
        except IntegrityError as e:
            # A translation activated concurrently collides with
            # the one written here. Nothing is written for this locale.
            log.warning(
                f"Pretranslations for locale {locale.code} not stored, "
                f"as a translation changed concurrently: {e!r}"
            )
            continue

        if written:
            update_pretranslated_resources(locale, written)

        log.info(f"Fetching pretranslations for locale {locale.code} done")

    log.info(f"Fetching pretranslations for project {project.name} done")


@shared_task(base=PontoonTask, name="pretranslate")
def pretranslate_task(project_pk):
    project = Project.objects.get(pk=project_pk)
    lock_name = f"pretranslate_{project_pk}"
    if not cache.add(lock_name, True, timeout=settings.SYNC_TASK_TIMEOUT):
        raise RuntimeError(
            f"Cannot pretranslate {project.slug} because its previous pretranslation is still running."
        )
    try:
        pretranslate(project, None)
    finally:
        # release the lock
        cache.delete(lock_name)
