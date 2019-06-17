from django.utils import timezone
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from bulk_update.helper import bulk_update

import pontoon.base as base
from pontoon.machinery.utils import google_translate_util, translation_memory_util
# from pontoon.base.models import Entity, Locale, Translation, TranslatedResource, User


def pretranslate(project, locales=None, entities=None):
    """
    Identifies strings without any translations and any suggestions.
    Engages TheAlgorithm (bug 1552796) to gather pre-translations.
    Stores pre-translations as suggestions (approved=False) to DB.
    Author should be set to a name like "Pontoon Translator <pontoon@mozilla.com>".
    Stats and Latest activity should be updated

    """

    if not locales:
        locales = project.locales.filter(project_locale__readonly=False)

    if not entities:
        entities = base.models.Entity.objects.filter(
            resource__project=project,
            obsolete=False,
        )

    now = timezone.now()

    resources = project.resources.filter(obsolete=False)

    user, created = base.models.User.objects.get_or_create(
        email = "pontoon@mozilla.com",
        username = "Pontoon-Translator",
    )

    locale_entities = base.models.Translation.objects.filter(
            locale__in=locales,
            entity__in=entities
        ).annotate(
            locale_entity=Concat('locale_id', V('-'), 'entity_id',output_field=CharField())
        ).values_list('locale_entity', flat=True).distinct()

    locale_entities = list(locale_entities)

    translations = []

    locale_list = []
    translatedresource_dict = {}
    projectlocale_list = []

    for locale in locales:
        for entity in entities:
            locale_entity = '{}-{}'.format(locale.id, entity.id)
            if not locale_entity in locale_entities:
                string = ""
                tm_response = translation_memory_util(
                    text=entity.string,
                    locale=locale,
                    max_results=5,
                )

                if tm_response and int(float(tm_response[0]['quality'])) == 100:
                    string = tm_response[0]['target']

                elif locale.google_translate_code:
                    gt_response = google_translate_util(
                        text=entity.string,
                        locale_code=locale.google_translate_code,
                    )

                    if 'translation' in gt_response.keys():
                        string = gt_response['translation']

                if string:
                    t = base.models.Translation(
                        entity=entity,
                        locale=locale,
                        string=string,
                        user=user,
                        date=now,
                        approved=False,
                        active=True,
                    )
                    translations.append(t)
                    locale_resource = '{}-{}'.format(locale.id, entity.resource.id)

                    if not locale_resource in translatedresource_dict.keys():
                        translatedresource = base.models.TranslatedResource.objects.get(
                            resource=entity.resource,
                            locale=locale
                        )
                        translatedresource_dict[locale_resource] = translatedresource




    translations = base.models.Translation.objects.bulk_create(translations)

    # update latest activity once and for all
    if len(translations)>0:
        project.latest_translation = translations[0]
        project.save(update_fields=['latest_translation'])

    # for locale in locale_list:
    #     locale.save(update_fields=['latest_translation'])

    # for projectlocale in projectlocale_list:
    #     projectlocale.save(update_fields=['latest_translation'])

    # bulk_update(locale_list, update_fields=['latest_translation'])
    # bulk_update(projectlocale_list, update_fields=['latest_translation'])
    # bulk_update(translatedresource_dict.values(), update_fields=['latest_translation'])

    for translation in translations:
        translation.update_latest_translation()

    for translatedresource in translatedresource_dict.values():
        # translatedresource.save(update_fields=['latest_translation'])
        translatedresource.calculate_stats()
