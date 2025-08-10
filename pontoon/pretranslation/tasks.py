import logging
import operator

from functools import reduce

from celery import shared_task

from django.conf import settings
from django.core.cache import cache
from django.db.models import CharField, Q, Value as V
from django.db.models.functions import Concat

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    Entity,
    Project,
    TranslatedResource,
    Translation,
    User,
)
from pontoon.base.tasks import PontoonTask
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import bulk_run_checks

from . import AUTHORS
from .pretranslate import get_pretranslation


log = logging.getLogger(__name__)


def pretranslate(project: Project, paths: set[str] | None):
    """
    Identifies strings without any translations and any suggestions.
    Engages TheAlgorithm (bug 1552796) to gather pretranslations.
    Stores pretranslations as suggestions (approved=False) to DB.

    :arg project: The project to be pretranslated
    :arg paths: Paths of the project resources to be pretranslated,
      or None to pretranslate all resources.

    :returns: None
    """
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

    # Fetch all locale-entity pairs with non-rejected or pretranslated translations
    pt_authors = {key: User.objects.get(email=email) for key, email in AUTHORS.items()}
    translated_entities = (
        Translation.objects.filter(
            locale__in=locales,
            entity__in=entities,
        )
        .filter(Q(rejected=False) | Q(user__in=pt_authors.values()))
        .annotate(
            locale_entity=Concat(
                "locale_id", V("-"), "entity_id", output_field=CharField()
            )
        )
        .values_list("locale_entity", flat=True)
        .distinct()
    )

    translated_entities = list(translated_entities)

    for locale in locales:
        log.info(f"Fetching pretranslations for locale {locale.code} started")

        translations = []

        # To keep track of changed TranslatedResources and their latest_translation
        tr_dict = {}
        tr_filter = []
        index = -1

        for entity in entities:
            locale_entity = f"{locale.id}-{entity.id}"
            locale_resource = f"{locale.id}-{entity.resource.id}"
            if locale_entity in translated_entities or locale_resource not in tr_pairs:
                continue

            try:
                pretranslation = get_pretranslation(entity, locale)
            except ValueError as e:
                log.info(f"Pretranslation error: {e}")
                continue

            failed_checks = run_checks(
                entity,
                locale.code,
                entity.string,
                pretranslation[0],
                use_tt_checks=False,
            )

            if failed_checks:
                try:
                    pretranslation = get_pretranslation(
                        entity, locale, preserve_placeables=True
                    )
                except ValueError as e:
                    log.info(f"Pretranslation error: {e}")
                    continue

            t = Translation(
                entity=entity,
                locale=locale,
                string=pretranslation[0],
                user=pt_authors[pretranslation[1]],
                approved=False,
                pretranslated=True,
                active=True,
            )

            index += 1
            translations.append(t)

            if locale_resource not in tr_dict:
                tr_dict[locale_resource] = index

                # Add query for fetching respective TranslatedResource.
                tr_filter.append(
                    Q(locale__id=locale.id) & Q(resource__id=entity.resource.id)
                )

            # Update the latest translation index
            tr_dict[locale_resource] = index

        if len(translations) == 0:
            log.info(
                f"Fetching pretranslations for locale {locale.code} done: No pretranslation fetched"
            )
            continue

        translations = Translation.objects.bulk_create(translations)

        # Log creating actions
        actions_to_log = [
            ActionLog(
                action_type=ActionLog.ActionType.TRANSLATION_CREATED,
                performed_by=t.user,
                translation=t,
            )
            for t in translations
        ]

        ActionLog.objects.bulk_create(actions_to_log)

        # Run checks on all translations
        translation_pks = {translation.pk for translation in translations}
        bulk_run_checks(Translation.objects.for_checks().filter(pk__in=translation_pks))

        # Mark translations as changed
        changed_translations = Translation.objects.filter(
            pk__in=translation_pks,
            # Do not sync translations with errors and warnings
            errors__isnull=True,
            warnings__isnull=True,
        )
        changed_translations.bulk_mark_changed()

        # Update latest activity and stats for changed instances.
        # `operator.ior` is the '|' Python operator, which turns into a logical OR
        # when used between django ORM query objects.
        tr_query = reduce(operator.ior, tr_filter)
        translatedresources = TranslatedResource.objects.filter(tr_query).annotate(
            locale_resource=Concat(
                "locale_id", V("-"), "resource_id", output_field=CharField()
            )
        )
        translatedresources.calculate_stats()
        for tr in translatedresources:
            index = tr_dict[tr.locale_resource]
            translation = translations[index]
            translation.update_latest_translation()

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
