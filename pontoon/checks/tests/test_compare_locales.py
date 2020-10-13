# coding: utf-8
import os

from textwrap import dedent

import pytest
from mock import MagicMock

from pontoon.checks.libraries.compare_locales import (
    CompareDTDEntity,
    cast_to_compare_locales,
    ComparePropertiesEntity,
    UnsupportedResourceTypeError,
    run_checks,
)


def mock_quality_check_args(
    resource_ext="",
    translation="",
    resource_entities=None,
    resource_path=None,
    **entity_data
):
    """
    Generate a dictionary of arguments ready to use by get_quality_check
    function.
    """
    entity = MagicMock()
    entity.key = "entity_a"
    if resource_path:
        entity.resource.path = resource_path
        entity.resource.format = os.path.splitext(resource_path)[1][1:]
    else:
        entity.resource.path = "resource1.{}".format(resource_ext)
        entity.resource.format = resource_ext
    entity.comment = ""
    res_entities = []

    for res_entity in resource_entities or []:
        res_mock_entity = MagicMock()
        res_mock_entity.comment = ""

        for k, v in res_entity.items():
            setattr(res_mock_entity, k, v)

        res_entities.append(res_mock_entity)

    entity.resource.entities.all.return_value = res_entities

    for k, v in entity_data.items():
        setattr(entity, k, v)

    return {
        "entity": entity,
        "locale_code": "en-US",
        "string": translation,
    }


@pytest.yield_fixture
def entity_with_comment(entity_a):
    """
    A simple entity that contains pre-defined key and comment.
    """
    entity_a.key = "key_entity_a"
    entity_a.comment = "example comment"
    return entity_a


@pytest.yield_fixture
def plural_entity(entity_with_comment):
    """
    Entity with plural string.
    """
    entity_with_comment.key = "key_entity_a"
    entity_with_comment.string_plural = "plural entity_a"
    entity_with_comment.comment = "example comment"
    return entity_with_comment


@pytest.yield_fixture
def plural_translation(translation_a):
    translation_a.plural_form = 1
    translation_a.string = "Plural translation for entity_a"
    return translation_a


def test_unsupported_resource_file():
    """
    Fail if passed resource is not supported by the integration with
    compare-locales.
    """
    with pytest.raises(UnsupportedResourceTypeError):
        cast_to_compare_locales(".random_ext", None, None)


@pytest.mark.django_db
def test_cast_to_properties(entity_with_comment, translation_a, entity_a):
    """
    Cast entities from .properties resources to PropertiesEntity
    """
    refEnt, transEnt = cast_to_compare_locales(
        ".properties", entity_with_comment, translation_a.string
    )

    assert isinstance(refEnt, ComparePropertiesEntity)
    assert isinstance(transEnt, ComparePropertiesEntity)

    assert refEnt.key == "key_entity_a"
    assert refEnt.val == entity_a.string
    assert refEnt.pre_comment.all == "example comment"

    assert transEnt.key == "key_entity_a"
    assert transEnt.val == "Translation for entity_a"
    assert transEnt.pre_comment.all == "example comment"


@pytest.mark.django_db
def test_cast_to_dtd(entity_with_comment, translation_a, entity_a):
    """
    Cast entities from .dtd resources to DTDEntity
    """
    refEnt, transEnt = cast_to_compare_locales(
        ".dtd", entity_with_comment, translation_a.string
    )

    assert isinstance(refEnt, CompareDTDEntity)
    assert isinstance(transEnt, CompareDTDEntity)

    assert refEnt.key == "key_entity_a"
    assert refEnt.val == entity_a.string
    assert refEnt.pre_comment.all == "example comment"
    assert refEnt.all == '<!ENTITY key_entity_a "%s">' % entity_a.string

    assert transEnt.key == "key_entity_a"
    assert transEnt.val == "Translation for entity_a"
    assert transEnt.pre_comment.all == "example comment"
    assert transEnt.all == '<!ENTITY key_entity_a "Translation for entity_a">'


@pytest.mark.parametrize(
    "quality_check_args",
    (
        mock_quality_check_args(
            resource_ext="properties", string="Foobar2", translation="Barfoo2"
        ),
        mock_quality_check_args(
            resource_ext="properties",
            string="Mozilla",
            string_plural="Mozillas",
            translation="Allizom",
        ),
        mock_quality_check_args(
            resource_ext="properties", string=u"モジラ", translation=u"モジラ translation",
        ),
        mock_quality_check_args(
            resource_ext="dtd", string=u"モジラ", translation=u"モジラ translation",
        ),
        mock_quality_check_args(
            resource_ext="ftl",
            string=u"entity = モジラ",
            translation=u"entity = モジラ translation",
        ),
    ),
)
def test_valid_translations(quality_check_args):
    """
    Quality check should return an empty dict if there's no errors.
    """
    assert run_checks(**quality_check_args) == {}


@pytest.mark.parametrize(
    "quality_check_args,failed_checks",
    (
        (
            mock_quality_check_args(
                resource_ext="properties",
                string="%s Foo %s bar %s",
                translation="%d Bar %d foo %d \\q %",
            ),
            {
                "clWarnings": [u"unknown escape sequence, \\q"],
                "clErrors": ["Found single %"],
            },
        ),
        (
            mock_quality_check_args(
                resource_ext="properties",
                string="Invalid #1 entity",
                comment="Localization_and_Plurals",
                translation="Invalid #1;translation #2",
            ),
            {"clErrors": ["unreplaced variables in l10n"]},
        ),
        (
            mock_quality_check_args(
                resource_ext="properties",
                string="Multi plural entity",
                comment="Localization_and_Plurals",
                translation="translation1;translation2;translation3",
            ),
            {"clWarnings": ["expecting 2 plurals, found 3"]},
        ),
    ),
)
def test_invalid_properties_translations(quality_check_args, failed_checks):
    assert run_checks(**quality_check_args) == failed_checks


@pytest.mark.django_db
@pytest.mark.parametrize(
    "quality_check_args,failed_checks",
    (
        (
            mock_quality_check_args(
                resource_ext="dtd",
                key="test",
                string="2005",
                translation="not a number",
            ),
            {"clWarnings": ["reference is a number"]},
        ),
        (
            mock_quality_check_args(
                resource_ext="dtd",
                key="test",
                string="Second &aa; entity",
                translation="Testing &NonExistingKey; translation",
                resource_entities=[
                    {"key": "validProductName", "string": "Firefox"},
                    {"key": "aa", "string": "bb &validProductName;"},
                    {"key": "cc", "string": "dd &aa;"},
                ],
            ),
            {
                "clWarnings": [
                    u"Referencing unknown entity `NonExistingKey`"
                    u" (aa used in context, validProductName known)",
                ],
            },
        ),
        (
            mock_quality_check_args(
                resource_ext="dtd",
                key="test",
                string="Valid entity",
                translation="&validProductName; translation",
                resource_entities=[
                    {"key": "validProductName", "string": "Firefox"},
                    {"key": "hello", "string": "hello &validProductName;"},
                ],
            ),
            {},
        ),
        (
            mock_quality_check_args(
                resource_ext="dtd",
                key="test",
                string="&validProductName; - 2017",
                comment="Some comment",
                translation="Valid translation",
                resource_entities=[
                    {"key": "validProductName", "string": "Firefox"},
                    {"key": "hello", "string": "hello &validProductName;"},
                ],
            ),
            {},
        ),
        (
            mock_quality_check_args(
                resource_ext="dtd",
                key="test",
                string="Mozilla 2017",
                comment="Some comment",
                translation="< translation",
            ),
            {"clErrors": ["not well-formed (invalid token)"]},
        ),
    ),
)
def test_invalid_dtd_translations(quality_check_args, failed_checks):
    assert run_checks(**quality_check_args) == failed_checks


def test_dtd_source_string_with_quotes():
    """
    A correct source string with quotes shouldn't raise a warning.
    """
    quality_check_args = mock_quality_check_args(
        resource_path="mobile/android/base/android_strings.dtd",
        key="test",
        string='Mozilla "2017"',
        comment="Some comment",
        translation='Mozilla "2018"',
    )
    assert run_checks(**quality_check_args) == {}


def test_dtd_entity_with_quotes():
    quality_check_args = mock_quality_check_args(
        resource_path="strings.dtd",
        key="test",
        string='<a href="http://mozilla.org">Mozilla</a>',
        comment="Some comment",
        translation='<a href="http://mozilla.org">Mozilla "2018"</a>',
    )
    assert run_checks(**quality_check_args) == {}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "quality_check_args,failed_checks",
    (
        (
            mock_quality_check_args(
                resource_ext="ftl",
                string=dedent(
                    """
                brandName = Firefox
                    .bar = foo
                """
                ),
                translation=dedent(
                    """
                brandName = Quantum
                """
                ),
            ),
            {"clErrors": ["Missing attribute: bar"]},
        ),
        (
            mock_quality_check_args(
                resource_ext="ftl",
                string=dedent(
                    """
                windowTitle = Old translations
                """
                ),
                translation=dedent(
                    """
                windowTitle = New translations
                    .baz = Fuz
                """
                ),
            ),
            {"clErrors": ["Obsolete attribute: baz"]},
        ),
        (
            mock_quality_check_args(
                resource_ext="ftl",
                string=dedent(
                    """
                windowTitle = Old translations
                    .baz = Fuz
                """
                ),
                translation=dedent(
                    """
                windowTitle =
                    .baz = Fuz
                """
                ),
            ),
            {"clErrors": ["Missing value"]},
        ),
        (
            mock_quality_check_args(
                resource_ext="ftl",
                string=dedent(
                    """
                windowTitle = Old translations
                    .pontoon = is cool
                """
                ),
                translation=dedent(
                    """
                windowTitle = New translations
                    .pontoon = pontoon1
                    .pontoon = pontoon2
                """
                ),
            ),
            {"clWarnings": ['Attribute "pontoon" is duplicated']},
        ),
    ),
)
def test_invalid_ftl_translations(quality_check_args, failed_checks):
    assert run_checks(**quality_check_args) == failed_checks
