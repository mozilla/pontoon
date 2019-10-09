import logging

from django.db.models import Q, CharField, Value as V
from django.db.models.functions import Concat

import pontoon.base as base
from pontoon.pretranslation.pretranslate import get_translations, update_changed_instances


log = logging.getLogger(__name__)


def pretranslate(project, locales=None, entities=None):
    """
    Identifies strings without any translations and any suggestions.
    Engages TheAlgorithm (bug 1552796) to gather pretranslations.
    Stores pretranslations as suggestions (approved=False) to DB.

    :arg Project project: the project to be pretranslated
    :arg Queryset locales: the locales for the project to be pretranslated
    :arg Queryset entites: the entities for the project to be pretranslated

    :returns: None
    """

    log.info('Fetching pretranslations for project {} started'.format(project.name))

    if not locales:
        locales = project.locales.filter(
            project_locale__readonly=False,
        ).prefetch_project_locale(project)

    if not entities:
        entities = base.models.Entity.objects.filter(
            resource__project=project,
            obsolete=False,
        ).prefetch_related('resource')

    # get available TranslatedResource pairs
    tr_pairs = base.models.TranslatedResource.objects.filter(
        resource__project=project,
        locale__in=locales,
    ).annotate(
        locale_resource=Concat('locale_id', V('-'), 'resource_id', output_field=CharField())
    ).values_list('locale_resource', flat=True).distinct()

    # Fetch all distinct locale-entity pairs for which translation exists
    translated_entities = base.models.Translation.objects.filter(
        locale__in=locales,
        entity__in=entities,
    ).annotate(
        locale_entity=Concat('locale_id', V('-'), 'entity_id', output_field=CharField())
    ).values_list('locale_entity', flat=True).distinct()

    translated_entities = list(translated_entities)

    translations = []

    # To keep track of changed Locales and TranslatedResources
    # Also, their latest_translation and stats count
    locale_dict = {}
    tr_dict = {}

    tr_filter = []
    index = -1

    for locale in locales:
        log.info('Fetching pretranslations for locale {} started'.format(locale.code))
        for entity in entities:
            locale_entity = '{}-{}'.format(locale.id, entity.id)
            locale_resource = '{}-{}'.format(locale.id, entity.resource.id)
            if locale_entity in translated_entities or locale_resource not in tr_pairs:
                continue

            strings = get_translations(entity, locale)

            if not strings:
                continue

            for string, plural_form, user in strings:
                t = base.models.Translation(
                    entity=entity,
                    locale=locale,
                    string=string,
                    user=user,
                    approved=False,
                    active=True,
                    plural_form=plural_form,
                )

                translations.append(t)

                index += 1

                if locale_resource not in tr_dict:
                    tr_dict[locale_resource] = [index, 0]
                    # Add query for fetching respective TranslatedResource.
                    tr_filter.append(
                        Q(locale__id=locale.id)
                        & Q(resource__id=entity.resource.id)
                    )

                if locale.code not in locale_dict:
                    locale_dict[locale.code] = [locale, index, 0]

                # Update the latest translation index
                tr_dict[locale_resource][0] = index
                locale_dict[locale.code][1] = index

                # Increment number of translations (used to adjust stats)
                tr_dict[locale_resource][1] += 1
                locale_dict[locale.code][2] += 1
        log.info('Fetching pretranslations for locale {} done'.format(locale.code))

    if len(translations) == 0:
        return

    translations = base.models.Translation.objects.bulk_create(translations)

    # Update latest activity and unreviewed count for the project.
    project.latest_translation = translations[-1]
    project.unreviewed_strings += len(translations)
    project.save(update_fields=['latest_translation', 'unreviewed_strings'])

    # Update latest activity and unreviewed count for changed instances.
    update_changed_instances(tr_filter, tr_dict, locale_dict, translations)

    log.info('Fetching pretranslations for project {} done'.format(project.name))
