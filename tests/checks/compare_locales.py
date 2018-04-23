from __future__ import absolute_import
from textwrap import dedent

import pytest
from mock import MagicMock

from pontoon.checks.libraries.compare_locales import (
    CompareDTDEntity,
    cast_to_compare_locales,
    ComparePropertiesEntity,
    CommentEntity,
    UnsupportedResourceTypeError,
    run_checks,
)


def mock_quality_check_args(
    resource_ext='',
    translation='',
    resource_entities=None,
    **entity_data
):
    """
    Generate a dictionary of arguments ready to use by get_quality_check function.
    """
    entity = MagicMock()
    entity.resource.path = 'resource1.{}'.format(resource_ext)
    entity.resource.format = resource_ext
    entity.comment = ''
    res_entities = []

    for res_entity in (resource_entities or []):
        res_mock_entity = MagicMock()
        res_mock_entity.comment = ''

        for k, v in res_entity.items():
            setattr(res_mock_entity, k, v)

        res_entities.append(res_mock_entity)

    entity.resource.entities.all.return_value = res_entities

    for k, v in entity_data.items():
        setattr(entity, k, v)

    return {
        'entity': entity,
        'locale': 'en-US',
        'string': translation,
    }


@pytest.yield_fixture
def entity_with_comment(entity0):
    """
    A simple entity that contains pre-defined key and comment.
    """
    entity0.key = 'KeyEntity0'
    entity0.comment = 'example comment'
    return entity0


@pytest.yield_fixture
def plural_entity(entity_with_comment):
    """
    Entity with plural string.
    """
    entity_with_comment.key = 'KeyEntity0'
    entity_with_comment.string_plural = 'plural entity0'
    entity_with_comment.comment = 'example comment'
    return entity_with_comment


@pytest.yield_fixture
def plural_translation(translation0):
    translation0.plural_form = 1
    translation0.string = 'Plural translation for entity0'
    return translation0


def test_unsupported_resource_file():
    """
    Fail if passed resource is not supported by the integration with compare-locales.
    """
    with pytest.raises(UnsupportedResourceTypeError):
        cast_to_compare_locales('.random_ext', None, None)


@pytest.mark.django_db
def test_cast_to_properties(entity_with_comment, translation0):
    """
    Cast entities from .properties resources to PropertiesEntity
    """
    refEnt, transEnt = cast_to_compare_locales(
        '.properties',
        entity_with_comment,
        translation0.string
    )

    assert isinstance(refEnt, ComparePropertiesEntity)
    assert isinstance(transEnt, ComparePropertiesEntity)

    assert refEnt.key == 'KeyEntity0'
    assert refEnt.val == 'entity0'
    assert refEnt.pre_comment.all == 'example comment'

    assert transEnt.key == 'KeyEntity0'
    assert transEnt.val == 'Translation for entity0'
    assert transEnt.pre_comment.all == 'example comment'


@pytest.mark.django_db
def test_cast_to_dtd(entity_with_comment, translation0):
    """
    Cast entities from .dtd resources to DTDEntity
    """
    refEnt, transEnt = cast_to_compare_locales(
        '.dtd',
        entity_with_comment,
        translation0.string
    )

    assert isinstance(refEnt, CompareDTDEntity)
    assert isinstance(transEnt, CompareDTDEntity)

    assert refEnt.key == 'KeyEntity0'
    assert refEnt.val == 'entity0'
    assert refEnt.pre_comment.all == 'example comment'
    assert refEnt.all == '<!ENTITY KeyEntity0 "entity0">'

    assert transEnt.key == 'KeyEntity0'
    assert transEnt.val == 'Translation for entity0'
    assert transEnt.pre_comment.all == 'example comment'
    assert transEnt.all == '<!ENTITY KeyEntity0 "Translation for entity0">'


@pytest.mark.parametrize(
    'quality_check_args', (
        mock_quality_check_args(
            resource_ext='properties',
            string='Foobar2',
            translation='Barfoo2'
        ),
        mock_quality_check_args(
            resource_ext='properties',
            string='Mozilla',
            string_plural='Mozillas',
            translation='Allizom',
            plural_form=1
        ),
    )
)
def test_valid_translations(quality_check_args):
    """
    Quality check should return an empty dict if there's no errors.
    """
    assert run_checks(**quality_check_args) == {}


@pytest.mark.parametrize(
    'quality_check_args,failed_checks',
    (
        (
            mock_quality_check_args(
                resource_ext='properties',
                string='%s Foo %s bar %s',
                translation='%d Bar %d foo %d \q %',
            ),
            {
                'clWarnings': [u'unknown escape sequence, \\q'],
                'clErrors': ['Found single %']
            }
        ),
        (
            mock_quality_check_args(
                resource_ext='properties',
                string='Invalid #1 entity',
                comment='Localization_and_Plurals',
                translation='Invalid #1;translation #2',
            ),
            {
                'clErrors': ['unreplaced variables in l10n']
            }
        ),
        (
            mock_quality_check_args(
                resource_ext='properties',
                string='Multi plural entity',
                comment='Localization_and_Plurals',
                translation='translation1;translation2;translation3',
            ),
            {
                'clWarnings': ['expecting 2 plurals, found 3'],
            }
        )
    )
)
def test_invalid_properties_translations(quality_check_args, failed_checks):
    assert run_checks(**quality_check_args) == failed_checks


@pytest.mark.django_db
@pytest.mark.parametrize(
    'quality_check_args,failed_checks',
    (
        (
            mock_quality_check_args(
                resource_ext='dtd',
                key='test',
                string='2005',
                translation='not a number',
            ),
            {
                'clWarnings': ['reference is a number'],
            },
        ),
        (
            mock_quality_check_args(
                resource_ext='dtd',
                key='test',
                string='Second &aa; entity',
                translation='Testing &NonExistingKey; translation',
                resource_entities=[
                    {
                        'key': 'validProductName',
                        'string': 'Firefox'
                    },
                    {
                        'key': 'aa',
                        'string': 'bb &validProductName;'
                    },
                    {
                        'key': 'cc',
                        'string': 'dd &aa;'
                    },
                ]
            ),
            {
                'clWarnings': [u'Referencing unknown entity `NonExistingKey`'
                               u' (aa used in context, validProductName known)'],
            },
        ),
        (
            mock_quality_check_args(
                resource_ext='dtd',
                key='test',
                string='Valid entity',
                translation='&validProductName; translation',
                resource_entities=[
                    {
                        'key': 'validProductName',
                        'string': 'Firefox'
                    },
                    {
                        'key': 'hello',
                        'string': 'hello &validProductName;'
                    },
                ]
            ),
            {},
        ),
        (
            mock_quality_check_args(
                resource_ext='dtd',
                key='test',
                string='&validProductName; - 2017',
                comment='Some comment',
                translation='Valid translation',
                resource_entities=[
                    {
                        'key': 'validProductName',
                        'string': 'Firefox'
                    },
                    {
                        'key': 'hello',
                        'string': 'hello &validProductName;'
                    },
                ]
            ),
            {},
        ),
        (
            mock_quality_check_args(
                resource_ext='dtd',
                key='test',
                string='Mozilla 2017',
                comment='Some comment',
                translation='< translation',
            ),
            {
                'clErrors': ['not well-formed (invalid token)']
            },
        ),
    )
)
def test_invalid_dtd_translations(quality_check_args, failed_checks):
    assert run_checks(**quality_check_args) == failed_checks


@pytest.mark.django_db
@pytest.mark.parametrize(
    'quality_check_args,failed_checks',
    (
        (
            mock_quality_check_args(
                resource_ext='ftl',
                string=dedent("""
                brandName = Firefox
                    .bar = foo
                """),
                translation=dedent("""
                brandName = Quantum
                """),
            ),
            {
                'clErrors': ['Missing attribute: bar'],
            }
        ),
        (
            mock_quality_check_args(
                resource_ext='ftl',
                string=dedent("""
                windowTitle = Old translations
                """),
                translation=dedent("""
                windowTitle = New translations
                    .baz = Fuz
                """),
            ),
            {
                'clErrors': ['Obsolete attribute: baz'],
            }
        ),
        (
            mock_quality_check_args(
                resource_ext='ftl',
                string=dedent("""
                windowTitle = Old translations
                    .baz = Fuz
                """),
                translation=dedent("""
                windowTitle
                    .baz = Fuz
                """),
            ),
            {
                'clErrors': ['Missing value']
            }
        ),
        (
            mock_quality_check_args(
                resource_ext='ftl',
                string=dedent("""
                windowTitle = Old translations
                    .pontoon = is cool
                """),
                translation=dedent("""
                windowTitle = New translations
                    .pontoon = pontoon1
                    .pontoon = pontoon2
                """),
            ),
            {
                'clWarnings': ['Attribute "pontoon" occurs 2 times']
            }
        )
    )
)
def test_invalid_ftl_translations(quality_check_args, failed_checks):
    assert run_checks(**quality_check_args) == failed_checks
