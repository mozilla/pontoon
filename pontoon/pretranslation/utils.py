from pontoon.machinery.utils import google_translate_util, translation_memory_util
# from pontoon.base.models import Entity, Locale, Translation, TranslatedResource, User
from django.utils import timezone
import pontoon.base as base


def pre_translate(project, locales=None, entities=None):
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
            translation__isnull=True,
        )

    now = timezone.now()

    resources = project.resources.filter(obsolete=False)

    user = base.models.User.objects.get(pk=2)
    for locale in locales:
        for entity in entities:
            string = ""
            tm_response = translation_memory_util(
                text=entity.string,
                locale=locale,
                max_results=5,
            )

            if tm_response and int(float(tm_response[0]['quality'])) is 100:
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
                )
                t.save()
                t.update_latest_translation()

        for resource in resources:
            translatedresource = base.models.TranslatedResource.objects.get(resource=resource, locale=locale)
            translatedresource.calculate_stats()
