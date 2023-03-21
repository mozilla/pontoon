import pytest

from fluent.syntax import FluentParser, FluentSerializer
from textwrap import dedent
from unittest.mock import patch

from pontoon.base.models import User
from pontoon.pretranslation.pretranslate import get_pretranslations
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    TranslationMemoryFactory,
)


parser = FluentParser()
serializer = FluentSerializer()


@pytest.fixture
def tm_user():
    return User.objects.get(email="pontoon-tm@example.com")


@pytest.fixture
def gt_user():
    return User.objects.get(email="pontoon-gt@example.com")


@pytest.fixture
def fluent_resource(project_a):
    return ResourceFactory(project=project_a, path="resource.ftl", format="ftl")


@pytest.mark.django_db
def test_get_pretranslations_no_match(entity_a, locale_b):
    # 100% TM match does not exist and locale.google_translate_code is None
    response = get_pretranslations(entity_a, locale_b)
    assert response == []


@pytest.mark.django_db
def test_get_pretranslations_empty_string(entity_a, locale_b, tm_user):
    # Entity.string is an empty string
    entity_a.string = ""
    response = get_pretranslations(entity_a, locale_b)
    assert response == [("", None, tm_user)]


@pytest.mark.django_db
def test_get_pretranslations_tm_match(entity_a, entity_b, locale_b, tm_user):
    # 100% TM match exists
    TranslationMemoryFactory.create(
        entity=entity_b,
        source=entity_a.string,
        target="tm_translation",
        locale=locale_b,
    )

    response = get_pretranslations(entity_a, locale_b)
    assert response == [("tm_translation", None, tm_user)]


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_gt_match(
    gt_mock, entity_a, google_translate_locale, gt_user
):
    # 100% TM match does not exist and locale.google_translate_code is not None
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    response = get_pretranslations(entity_a, google_translate_locale)
    assert response == [("gt_translation", None, gt_user)]


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_plurals(
    gt_mock, entity_a, google_translate_locale, gt_user
):
    # Entity.string_plural is not None
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    entity_a.string_plural = entity_a.string
    google_translate_locale.cldr_plurals = "1,2"

    response = get_pretranslations(entity_a, google_translate_locale)
    assert response == [
        ("gt_translation", 0, gt_user),
        ("gt_translation", 1, gt_user),
    ]


@pytest.mark.django_db
def test_get_pretranslations_fluent_no_match(fluent_resource, locale_b):
    # 100% TM match does not exist and locale.google_translate_code is None
    fluent_string = "hello-world = Hello World!"
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    response = get_pretranslations(fluent_entity, locale_b)
    assert response == []


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_simple(
    gt_mock, fluent_resource, google_translate_locale, gt_user
):
    # Entity.string is a simple Fluent string
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    fluent_string = "hello-world = Hello World!"
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)
    pretranslated_string = "hello-world = gt_translation\n"

    response = get_pretranslations(fluent_entity, google_translate_locale)
    assert response == [(pretranslated_string, None, gt_user)]


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_empty(
    gt_mock, fluent_resource, google_translate_locale, gt_user
):
    # Entity.string is an empty Fluent string
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    fluent_string = 'hello-world = { "" }'
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)
    pretranslated_string = "hello-world = gt_translation\n"

    response = get_pretranslations(fluent_entity, google_translate_locale)
    assert response == [(pretranslated_string, None, gt_user)]


@pytest.mark.django_db
def test_get_pretranslations_fluent_whitespace(
    fluent_resource, google_translate_locale, tm_user
):
    # Various types of whitespace should be preserved
    input_string = dedent(
        """
        whitespace =
            { $count ->
                [0] { "" }
                [1] { " " }
                *[other] { "\t" } { "\n" }
            }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    output_string = input_string

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(output_string))

    response = get_pretranslations(fluent_entity, google_translate_locale)
    assert response == [(pretranslated_string, None, tm_user)]


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_plural(
    gt_mock, fluent_resource, google_translate_locale, gt_user
):
    # Various types of whitespace should be preserved
    gt_mock.return_value = {
        "status": True,
        "translation": "GT",
    }

    google_translate_locale.cldr_plurals = "1,2,3,5"

    input_string = dedent(
        """
        plural =
            { $count ->
                [0] No matches found.
                [one] One match found.
                *[other] { $count } matches found.
            }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    expected = dedent(
        """
        plural =
            { $count ->
                [0] GT
                [one] GT
                [two] GT
                [few] GT
                *[other] GT
            }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslations(fluent_entity, google_translate_locale)
    assert response == [(pretranslated_string, None, gt_user)]


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_complex(
    gt_mock, entity_a, fluent_resource, google_translate_locale, tm_user
):
    # Entity.string is a complex Fluent string.
    # - Uplift selector and repeat shared parts within variants.
    # - Only translate text nodes.
    # - Service with most translated nodes is picked as translation author.
    gt_mock.return_value = {
        "status": True,
        "translation": "GT: Open Options and select Search.",
    }

    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Open Preferences and select Search.",
        target="TM: Open Preferences and select Search.",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Open Settings and select Search.",
        target="TM: Open Settings and select Search.",
        locale=google_translate_locale,
    )

    fluent_string = dedent(
        """
        complex-entry =
            Open { PLATFORM() ->
                [mac] Preferences
                [win] Settings
                *[other] Options
            } and select Search.
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    expected = dedent(
        """
        complex-entry =
            { PLATFORM() ->
                [mac] TM: Open Preferences and select Search.
                [win] TM: Open Settings and select Search.
                *[other] GT: Open Options and select Search.
            }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslations(fluent_entity, google_translate_locale)
    assert response == [(pretranslated_string, None, tm_user)]


# This test will fail, because pontoon.base.fluent.FlatTransformer moves trailing
# space between selectors into selector variants, but it gets lost in pretranslation
# due to re-serialization.
#
# Unless escaped, trailing space is not significant. So we should modify the
# FlatTransformer to escape it or, even better, use nested selectors as in the translate
# view, in which case we don't need trailing space at all.
@pytest.mark.xfail
@pytest.mark.django_db
def test_get_pretranslations_fluent_sibling_selectors(
    entity_a, fluent_resource, google_translate_locale, tm_user
):
    # Entity.string is a Fluent string with two sibling selectors.
    # - Move any text outside selectors into selector variants.
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $key_count } key and ",
        target="TM: { $key_count } key and ",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $key_count } keys and ",
        target="TM: { $key_count } keys and ",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $lock_count } lock",
        target="TM: { $lock_count } lock",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $lock_count } locks",
        target="TM: { $lock_count } locks",
        locale=google_translate_locale,
    )

    fluent_string = dedent(
        """
        sibling-selector =
            { $key_count ->
                [one] { $key_count } key
                *[other] { $key_count } keys
            } and { $lock_count ->
                [one] { $lock_count } lock
                *[other] { $lock_count } locks
            }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    expected = dedent(
        """
        sibling-selector =
            { $key_count ->
                [one] TM: { $key_count } key and
                *[other] TM: { $key_count } keys and
            }{ $lock_count ->
                [one] TM: { $lock_count } lock
                *[other] TM: { $lock_count } locks
            }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslations(fluent_entity, google_translate_locale)
    assert response == [(pretranslated_string, None, tm_user)]
