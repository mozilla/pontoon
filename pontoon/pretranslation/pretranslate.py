from functools import reduce
import operator

from django.db.models import CharField, Value as V
from django.db.models.functions import Concat

from pontoon.base.models import User, TranslatedResource
from pontoon.machinery.utils import (
    get_google_translate_data,
    get_translation_memory_data,
)


def get_translations(entity, locale):
    """
    Get pretranslations for the entity-locale pair

    :arg Entity entity: the Entity object
    :arg Locale locale: the Locale object

    :returns: a list of tuple with:
        - a pretranslation of the entity
        - plural form
        - user - tm_user/gt_user
    """
    tm_user = User.objects.get(email="pontoon-tm@example.com")
    gt_user = User.objects.get(email="pontoon-gt@example.com")

    strings = []
    plural_forms = range(0, locale.nplurals or 1)

    # Try to get matches from translation_memory
    tm_response = get_translation_memory_data(text=entity.string, locale=locale,)

    tm_response = [t for t in tm_response if int(t["quality"]) == 100]

    if tm_response:
        if entity.string_plural == "":
            strings = [(tm_response[0]["target"], None, tm_user)]
        else:
            for plural_form in plural_forms:
                strings.append((tm_response[0]["target"], plural_form, tm_user))

    # Else fetch from google translate
    elif locale.google_translate_code:
        gt_response = get_google_translate_data(
            text=entity.string, locale_code=locale.google_translate_code,
        )

        if gt_response["status"]:
            if entity.string_plural == "":
                strings = [(gt_response["translation"], None, gt_user)]
            else:
                for plural_form in plural_forms:
                    strings.append((gt_response["translation"], plural_form, gt_user))
    return strings


def update_changed_instances(tr_filter, tr_dict, translations):
    """
    Update the latest activity and stats for changed Locales, ProjectLocales
    & TranslatedResources
    """
    tr_filter = tuple(tr_filter)
    # Combine all generated filters with an OK operator.
    # `operator.ior` is the '|' Python operator, which turns into a logical OR
    # when used between django ORM query objects.
    tr_query = reduce(operator.ior, tr_filter)

    translatedresources = TranslatedResource.objects.filter(tr_query).annotate(
        locale_resource=Concat(
            "locale_id", V("-"), "resource_id", output_field=CharField()
        )
    )

    translatedresources.update_stats()

    for tr in translatedresources:
        index = tr_dict[tr.locale_resource]
        translation = translations[index]
        translation.update_latest_translation()
