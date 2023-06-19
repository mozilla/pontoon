import logging

from django.db.models import Q, CharField, Value as V
from django.db.models.functions import Concat
from django.conf import settings
from pontoon.base.models import (
    Project,
    Entity,
    TranslatedResource,
    Translation,
    User,
)
from pontoon.actionlog.models import ActionLog
from pontoon.pretranslation import AUTHORS
from pontoon.pretranslation.pretranslate import (
    get_pretranslations,
    update_changed_instances,
)
from pontoon.base.tasks import PontoonTask
from pontoon.sync.core import serial_task
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import bulk_run_checks


log = logging.getLogger(__name__)


@serial_task(settings.SYNC_TASK_TIMEOUT, base=PontoonTask, lock_key="project={0}")
def pretranslate(self, project_pk, locales=None, entities=None):
    """
    Identifies strings without any translations and any suggestions.
    Engages TheAlgorithm (bug 1552796) to gather pretranslations.
    Stores pretranslations as suggestions (approved=False) to DB.

    :arg project_pk: the pk of the project to be pretranslated
    :arg Queryset locales: the locales for the project to be pretranslated
    :arg Queryset entites: the entities for the project to be pretranslated

    :returns: None
    """
    project = Project.objects.get(pk=project_pk)

    if not project.pretranslation_enabled:
        log.info(f"Pretranslation not enabled for project {project.name}")
        return

    if locales:
        locales = project.locales.filter(pk__in=locales)
    else:
        locales = project.locales

    locales = locales.filter(
        project_locale__project=project,
        project_locale__pretranslation_enabled=True,
        project_locale__readonly=False,
    )

    if not locales:
        log.info(
            f"Pretranslation not enabled for any locale within project {project.name}"
        )
        return

    log.info(f"Fetching pretranslations for project {project.name} started")

    if not entities:
        entities = Entity.objects.filter(
            resource__project=project,
            obsolete=False,
        )

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
    pt_authors = [User.objects.get(email=email) for email in AUTHORS.values()]
    translated_entities = (
        Translation.objects.filter(
            locale__in=locales,
            entity__in=entities,
        )
        .filter(Q(rejected=False) | Q(user__in=pt_authors))
        .annotate(
            locale_entity=Concat(
                "locale_id", V("-"), "entity_id", output_field=CharField()
            )
        )
        .values_list("locale_entity", flat=True)
        .distinct()
    )

    translated_entities = list(translated_entities)

    translations = []

    # To keep track of changed TranslatedResources and their latest_translation
    tr_dict = {}

    tr_filter = []
    index = -1

    for locale in locales:
        log.info(f"Fetching pretranslations for locale {locale.code} started")
        for entity in entities:
            locale_entity = f"{locale.id}-{entity.id}"
            locale_resource = f"{locale.id}-{entity.resource.id}"
            if locale_entity in translated_entities or locale_resource not in tr_pairs:
                continue

            pretranslations = get_pretranslations(entity, locale)

            if not pretranslations:
                continue

            failed_checks = run_checks(
                entity,
                locale.code,
                entity.string,
                pretranslations[0][0],
                use_tt_checks=False,
            )

            if failed_checks:
                pretranslations = get_pretranslations(
                    entity, locale, preserve_placeables=True
                )

            for string, plural_form, user in pretranslations:
                t = Translation(
                    entity=entity,
                    locale=locale,
                    string=string,
                    user=user,
                    approved=False,
                    pretranslated=True,
                    active=True,
                    plural_form=plural_form,
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

        log.info(f"Fetching pretranslations for locale {locale.code} done")

    if len(translations) == 0:
        return

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
    update_changed_instances(tr_filter, tr_dict, translations)

    log.info(f"Fetching pretranslations for project {project.name} done")
