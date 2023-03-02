import operator

from fluent.syntax import FluentSerializer
from functools import reduce

from django.db.models import CharField, Value as V
from django.db.models.functions import Concat

from pontoon.base.models import User, TranslatedResource
from pontoon.machinery.utils import (
    get_google_translate_data,
    get_translation_memory_data,
)

from pontoon.base.templatetags.helpers import (
    as_simple_translation,
    is_single_input_ftl_string,
    get_reconstructed_message,
)

UNTRANSLATABLE_KEY = "AIzaSyDX3R5Y1kxh_8lJ4OAO"

serializer = FluentSerializer()


def get_pretranslations(entity, locale):
    """
    Get pretranslations for the entity-locale pair using internal translation memory and
    Google's machine translation.

    :arg Entity entity: the Entity object
    :arg Locale locale: the Locale object

    :returns: a list of tuples, consisting of:
        - a pretranslation of the entity
        - a plural form
        - a user (representing TM or GT)
    """
    tm_user = User.objects.get(email="pontoon-tm@example.com")
    gt_user = User.objects.get(email="pontoon-gt@example.com")

    strings = []
    plural_forms = range(0, locale.nplurals or 1)

    tm_input = (
        as_simple_translation(entity.string)
        if is_single_input_ftl_string(entity.string)
        else entity.string
    )

    # Return empty translation if source text empty
    if tm_input == "":
        return [("", None, tm_user)]

    # Try to get matches from translation_memory
    tm_response = get_translation_memory_data(
        text=tm_input,
        locale=locale,
    )

    tm_response = [t for t in tm_response if int(t["quality"]) == 100]

    if tm_response:
        if entity.string_plural == "":
            translation = tm_response[0]["target"]

            if entity.string != tm_input:
                translation = serializer.serialize_entry(
                    get_reconstructed_message(entity.string, translation)
                )

            strings = [(translation, None, tm_user)]
        else:
            for plural_form in plural_forms:
                strings.append((tm_response[0]["target"], plural_form, tm_user))

    # Else fetch from google translate
    elif locale.google_translate_code:
        gt_input = (
            entity.string.replace(entity.key, UNTRANSLATABLE_KEY, 1)
            if entity.resource.format == "ftl"
            else entity.string
        )

        gt_response = get_google_translate_data(
            text=gt_input,
            locale=locale,
        )

        if gt_response["status"]:
            if entity.string != gt_input:
                gt_response["translation"] = gt_response["translation"].replace(
                    UNTRANSLATABLE_KEY, entity.key
                )

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
