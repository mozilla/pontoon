from pontoon.base.models import Resource
from pontoon.translations.utils import parse_source_string_to_json


PLURAL_MF2 = (
    ".input {$n :number}\n"
    ".match $n\n"
    "one {{jedna rzecz}}\n"
    "few {{kilka rzeczy}}\n"
    "* {{wiele rzeczy}}\n"
)


def catchall_keys(value):
    return [
        key
        for variant in value["alt"]
        for key in variant["keys"]
        if isinstance(key, dict)
    ]


def test_plural_catchall_uses_locale_category():
    """For a locale whose last plural category is `many`, the catchall must be
    labelled `many` (#4453).
    """
    _, value, _ = parse_source_string_to_json(
        Resource.Format.GETTEXT, PLURAL_MF2, "many"
    )
    assert catchall_keys(value) == [{"*": "many"}]


def test_plural_catchall_defaults_to_other():
    """Without a catchall name, the catchall keeps the source locale's category."""
    _, value, _ = parse_source_string_to_json(Resource.Format.GETTEXT, PLURAL_MF2)
    assert catchall_keys(value) == [{"*": "other"}]


def test_plural_catchall_for_locale_ending_in_other():
    _, value, _ = parse_source_string_to_json(
        Resource.Format.GETTEXT, PLURAL_MF2, "other"
    )
    assert catchall_keys(value) == [{"*": "other"}]
