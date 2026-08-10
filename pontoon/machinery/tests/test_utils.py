from unittest.mock import MagicMock, patch

import pytest

from django.core.cache import cache
from django.core.management import call_command

from pontoon.base.models import Resource
from pontoon.machinery.utils import (
    get_google_automl_translation,
    get_llm_string_id,
    get_machinery_service_cache_key,
)
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ResourceFactory,
    SectionFactory,
)


@pytest.fixture
def automl_project_id(settings):
    settings.GOOGLE_AUTOML_PROJECT_ID = "test-project"
    return settings.GOOGLE_AUTOML_PROJECT_ID


@pytest.fixture
def automl_locale():
    return LocaleFactory(
        google_translate_code="kk",
        google_automl_model="TST123",
    )


def mock_automl_client(translated_text="target"):
    """Return a mocked TranslationServiceClient yielding a single translation."""
    translation = MagicMock(translated_text=translated_text)
    response = MagicMock(translations=[translation], glossary_translations=[])
    client = MagicMock()
    client.translate_text.return_value = response
    return client


@pytest.mark.django_db
def test_get_google_automl_translation_uses_cache(automl_project_id, automl_locale):
    cache.clear()

    with patch("pontoon.machinery.utils.translate") as mock_translate:
        mock_translate.TranslationServiceClient.return_value = mock_automl_client()

        first = get_google_automl_translation("t", automl_locale)
        # Second identical request should be served from cache
        second = get_google_automl_translation("t", automl_locale)

    assert first == second == "target"
    assert (
        mock_translate.TranslationServiceClient.return_value.translate_text.call_count
        == 1
    )


@pytest.mark.django_db
def test_get_google_automl_translation_bypasses_cache(automl_project_id, automl_locale):
    """
    With use_cache=False, the request must reach Google even when a cached value
    exists, and it must not pollute the cache.
    """
    cache.clear()
    cache_key = get_machinery_service_cache_key(
        "google_automl", "t", automl_locale.code, "text", False
    )
    cache.set(cache_key, "stale")

    with patch("pontoon.machinery.utils.translate") as mock_translate:
        client = mock_automl_client(translated_text="fresh")
        mock_translate.TranslationServiceClient.return_value = client

        result = get_google_automl_translation("t", automl_locale, use_cache=False)

    # The real client was hit despite the cached value...
    assert client.translate_text.call_count == 1
    assert result == "fresh"
    # ...and the cache was left untouched.
    assert cache.get(cache_key) == "stale"


@pytest.mark.django_db
def test_warmup_automl_command_bypasses_cache(automl_project_id, automl_locale):
    cache.clear()
    cache_key = get_machinery_service_cache_key(
        "google_automl", "t", automl_locale.code, "text", False
    )
    cache.set(cache_key, "stale")

    with patch("pontoon.machinery.utils.translate") as mock_translate:
        client = mock_automl_client()
        mock_translate.TranslationServiceClient.return_value = client

        call_command("warmup_automl")

    # The warmup made a real request even though a cached value was present.
    assert client.translate_text.call_count == 1


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
        # Parts identical to the source string are dropped: the id in XLIFF and
        # XCODE files, or the message id in gettext, optionally followed by the
        # message context
        (
            Resource.Format.XCODE,
            ["Localizable.strings"],
            ["Localizable.strings", "Open browser"],
            None,
        ),
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
