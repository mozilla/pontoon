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
    google_translate_locale.cldr_plurals = "1, 2"

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


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_complex(
    gt_mock, entity_a, fluent_resource, google_translate_locale, tm_user
):
    # Entity.string is a complex Fluent string.
    # Only translate text nodes.
    # Service with most translated nodes is picked as translation author.
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Preferences",
        target="tm_translation",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Settings",
        target="tm_translation",
        locale=google_translate_locale,
    )

    fluent_string = dedent(
        """
        my-entry =
            { PLATFORM() ->
                [mac] Preferences
                [win] Settings
                *[other] Options
            }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    expected = dedent(
        """
        my-entry =
            { PLATFORM() ->
                [mac] tm_translation
                [win] tm_translation
                *[other] gt_translation
            }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslations(fluent_entity, google_translate_locale)
    assert response == [(pretranslated_string, None, tm_user)]
