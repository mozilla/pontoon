from six.moves import reduce
import operator

from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from bulk_update.helper import bulk_update

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
    tm_user = User.objects.get(email="pontoon-tm@mozilla.com")
    gt_user = User.objects.get(email="pontoon-gt@mozilla.com")

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

    translatedresources = TranslatedResource.objects.filter(tr_query).annotate(
        locale_resource=Concat(
            "locale_id", V("-"), "resource_id", output_field=CharField()
        )
    )

    for tr in translatedresources:
        data = tr_dict[tr.locale_resource]
        tr.latest_translation = translations[data["latest_translation_index"]]
        tr.fuzzy_strings += data["fuzzy_translation_count"]
        tr.strings_with_warnings += data["warning_count"]
        tr.strings_with_errors += data["error_count"]
        tr_list.append(tr)

    for data in locale_dict.values():
        locale = data["locale"]
        projectlocale = locale.fetched_project_locale[0]

        locale.latest_translation = translations[data["latest_translation_index"]]
        projectlocale.latest_translation = translations[
            data["latest_translation_index"]
        ]

        # Since the translations fall into fuzzy category.
        locale.fuzzy_strings += data["fuzzy_translation_count"]
        projectlocale.fuzzy_strings += data["fuzzy_translation_count"]

        locale.strings_with_errors += data["error_count"]
        projectlocale.strings_with_errors += data["error_count"]

        locale.strings_with_warnings += data["warning_count"]
        projectlocale.strings_with_warnings += data["warning_count"]

        locale_list.append(locale)
        projectlocale_list.append(projectlocale)

    bulk_update(
        locale_list,
        update_fields=[
            "latest_translation",
            "fuzzy_strings",
            "strings_with_warnings",
            "strings_with_errors",
        ],
    )
    bulk_update(
        projectlocale_list,
        update_fields=[
            "latest_translation",
            "fuzzy_strings",
            "strings_with_warnings",
            "strings_with_errors",
        ],
    )
    bulk_update(
        tr_list,
        update_fields=[
            "latest_translation",
            "fuzzy_strings",
            "strings_with_warnings",
            "strings_with_errors",
        ],
    )
