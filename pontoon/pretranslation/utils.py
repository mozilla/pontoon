from six.moves import reduce
import operator
import logging

from django.utils import timezone
from django.db.models import Q, CharField, Value as V
from django.db.models.functions import Concat
from bulk_update.helper import bulk_update

import pontoon.base as base
from pontoon.machinery.utils import get_google_translate_data, get_translation_memory_data

log = logging.getLogger(__name__)


def get_translations(entity, locale):
    """
    Get pre-translations for the entity-locale pair

    :arg Entity entity: the Entity object
    :arg Locale locale: the Locale object

    :returns: a list of tuple with:
        - a pretranslation of the entity
        - plural form
        - user - tm_user/gt_user
    """
    tm_user = base.models.User.objects.get(email="pontoon-tm@mozilla.com")
    gt_user = base.models.User.objects.get(email="pontoon-gt@mozilla.com")

    strings = []
    plural_forms = range(0, locale.nplurals or 1)

    # Try to get matches from translation_memory
    tm_response = get_translation_memory_data(
        text=entity.string,
        locale=locale,
    )
    tm_response = [t for t in tm_response if int(t['quality']) == 100]
    tm_response = sorted(tm_response, key=lambda e: e['plural_form'])
    if tm_response:
        if entity.string_plural == "":
            strings = [(tm_response[0]['target'], None, tm_user)]
        else:
            for plural_form in plural_forms:
                strings.append((tm_response[0]['target'], plural_form, tm_user))

    # Else fetch from google translate
    elif locale.google_translate_code:
        gt_response = get_google_translate_data(
            text=entity.string,
            locale_code=locale.google_translate_code,
        )

        if gt_response['status']:
            if entity.string_plural == "":
                strings = [(gt_response['translation'], None, gt_user)]
            else:
                for plural_form in plural_forms:
                    strings.append((gt_response['translation'], plural_form, gt_user))
    return strings


def pretranslate(project, locales=None, entities=None):
    """
    Identifies strings without any translations and any suggestions.
    Engages TheAlgorithm (bug 1552796) to gather pre-translations.
    Stores pre-translations as suggestions (approved=False) to DB.

    :arg Project project: the project to be pre translated
    :arg Queryset locales: the locales for the project to be pre translated
    :arg Queryset entites: the entities for the project to be pre translated

    :returns: None
    """

    log.info("Fetching pretranslations for project {} started".format(project.name))

    if not locales:
        locales = project.locales.filter(
            project_locale__readonly=False,
        ).prefetch_project_locale(project)

    if not entities:
        entities = base.models.Entity.objects.filter(
            resource__project=project,
            obsolete=False,
        ).prefetch_related('resource')

    # Fetch all distinct locale-entity pairs for which translation exists
    translated_entities = base.models.Translation.objects.filter(
        locale__in=locales,
        entity__in=entities,
    ).annotate(
        locale_entity=Concat('locale_id', V('-'), 'entity_id', output_field=CharField())
    ).values_list('locale_entity', flat=True).distinct()

    translated_entities = list(translated_entities)

    now = timezone.now()

    translations = []

    # To keep track of changed Locales and TranslatedResources
    # Also, their latest_translation and stats count
    locale_dict = {}
    tr_dict = {}

    tr_filter = []
    index = -1

    for locale in locales:
        log.info("Fetching pretranslations for locale {} started".format(locale.code))
        for entity in entities:
            locale_entity = '{}-{}'.format(locale.id, entity.id)
            if locale_entity not in translated_entities:
                strings = get_translations(entity, locale)
                if strings:
                    for string, plural_form, user in strings:
                        t = base.models.Translation(
                            entity=entity,
                            locale=locale,
                            string=string,
                            user=user,
                            date=now,
                            approved=False,
                            active=True,
                            plural_form=plural_form,
                        )

                        translations.append(t)

                        index += 1

                        locale_resource = '{}-{}'.format(locale.id, entity.resource.id)
                        if locale_resource not in tr_dict:
                            tr_dict[locale_resource] = [index, 0]
                            # Add query for fetching respective TranslatedResource.
                            tr_filter.append(
                                Q(locale__id=locale.id)
                                & Q(resource__id=entity.resource.id)
                            )

                        if locale.code not in locale_dict:
                            locale_dict[locale.code] = [locale, index, 0]

                        # Increment number of translations (used to adjust stats)
                        tr_dict[locale_resource][1] += 1
                        locale_dict[locale.code][2] += 1
        log.info("Fetching pretranslations for locale {} done".format(locale.code))

    if len(translations) == 0:
        return

    translations = base.models.Translation.objects.bulk_create(translations)

    # Update latest activity and unreviewed count for the project.
    project.latest_translation = translations[0]
    project.unreviewed_strings += len(translations)
    project.save(update_fields=['latest_translation', 'unreviewed_strings'])

    # Update latest activity and unreviewed count for changed instances.
    update_changed_instances(tr_filter, tr_dict, locale_dict, translations)

    log.info("Fetching pretranslations for project {} done".format(project.name))


def update_changed_instances(tr_filter, tr_dict, locale_dict, translations):
    """
    Update the latest activity and stats for changed Locales, ProjectLocales
    & TranslatedResources
    """
    locale_list = []
    projectlocale_list = []
    tr_list = []

    tr_filter = tuple(tr_filter)
    # Combine all generated filters with an OK operator.
    # `operator.ior` is the '|' Python operator, which turns into a logical OR
    # when used between django ORM query objects.
    tr_query = reduce(operator.ior, tr_filter)

    translatedresources = base.models.TranslatedResource.objects.filter(
        tr_query
    ).annotate(
        locale_resource=Concat('locale_id', V('-'), 'resource_id', output_field=CharField())
    )

    for tr in translatedresources:
        index, diff = tr_dict[tr.locale_resource]
        tr.latest_translation = translations[index]
        tr.unreviewed_strings += diff
        tr_list.append(tr)

    for locale, index, diff in locale_dict.values():
        projectlocale = locale.fetched_project_locale[0]

        locale.latest_translation = translations[index]
        projectlocale.latest_translation = translations[index]

        # Since the translations fall into unreviewed category.
        locale.unreviewed_strings += diff
        projectlocale.unreviewed_strings += diff

        locale_list.append(locale)
        projectlocale_list.append(projectlocale)

    bulk_update(locale_list, update_fields=['latest_translation', 'unreviewed_strings'])
    bulk_update(projectlocale_list, update_fields=['latest_translation', 'unreviewed_strings'])
    bulk_update(tr_list, update_fields=['latest_translation', 'unreviewed_strings'])
