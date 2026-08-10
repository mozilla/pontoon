import pytest

from pontoon.base.models import Resource
from pontoon.machinery.openai_service import get_llm_string_id
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    SectionFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "format, section_key, entity_key, expected",
    [
        # Formats without a section key
        (Resource.Format.PROPERTIES, [], ["open-browser"], "open-browser"),
        # Formats with the file name or section name as the section key
        (
            Resource.Format.XLIFF,
            ["Client/Client.strings"],
            ["Client/Client.strings", "Settings.Title"],
            "Settings.Title",
        ),
        (
            Resource.Format.XCODE,
            ["Localizable.strings"],
            ["Localizable.strings", "Settings.Title"],
            "Settings.Title",
        ),
        (Resource.Format.INI, ["Strings"], ["Strings", "label"], "label"),
        (Resource.Format.ANDROID, ["!ENTITY"], ["!ENTITY", "brandName"], "brandName"),
        # For gettext, the message id is the source string, optionally
        # followed by the message context
        (Resource.Format.GETTEXT, [], ["Open browser"], None),
        (Resource.Format.GETTEXT, [], ["Open browser", "toolbar"], "toolbar"),
        # Nested keys are joined
        (
            Resource.Format.PLAIN_JSON,
            [],
            ["toolbar", "open-browser"],
            "toolbar.open-browser",
        ),
        # Missing key
        (Resource.Format.PROPERTIES, [], [], None),
    ],
)
def test_get_llm_string_id(format, section_key, entity_key, expected):
    resource = ResourceFactory(format=format)
    section = SectionFactory(key=section_key, resource=resource)
    entity = EntityFactory(
        key=entity_key, string="Open browser", resource=resource, section=section
    )

    assert get_llm_string_id(entity) == expected


@pytest.mark.django_db
def test_get_llm_string_id_without_section():
    resource = ResourceFactory(format=Resource.Format.PROPERTIES)
    entity = EntityFactory(key=["open-browser"], resource=resource, section=None)

    assert get_llm_string_id(entity) == "open-browser"
