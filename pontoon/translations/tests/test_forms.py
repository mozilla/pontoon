import pytest

from pontoon.translations.forms import CreateTranslationForm


@pytest.mark.django_db
def test_create_translation_form_required_fields():
    form = CreateTranslationForm({})
    assert not form.is_valid()
    assert form.errors["entity"]
    assert form.errors["entity"][0] == "This field is required."

    assert form.errors["locale"]
    assert form.errors["locale"][0] == "This field is required."

    assert "ignore_warnings" not in form.errors
    assert "approve" not in form.errors
    assert "force_suggestions" not in form.errors
    assert "paths" not in form.errors


@pytest.mark.django_db
def test_create_translation_form_clean_entity(entity_a, locale_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "value": ["salut"],
            "locale": locale_a.code,
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["entity"] == entity_a


@pytest.mark.django_db
def test_create_translation_form_clean_entity_invalid(locale_a):
    form = CreateTranslationForm(
        {
            "entity": 42,
            "translation": "salut",
            "value": ["salut"],
            "locale": locale_a.code,
        }
    )
    assert not form.is_valid()
    assert form.errors["entity"][0] == "Entity `42` could not be found"


@pytest.mark.django_db
def test_create_translation_form_clean_locale_invalid(entity_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "value": ["salut"],
            "locale": "invalid",
        }
    )
    assert not form.is_valid()
    assert form.errors["locale"][0] == "Locale `invalid` could not be found"


@pytest.mark.django_db
def test_create_translation_form_clean_locale(entity_a, locale_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "value": ["salut"],
            "locale": locale_a.code,
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["locale"] == locale_a


@pytest.mark.django_db
def test_create_translation_form_clean_stats(entity_a, locale_a):
    data = {
        "entity": entity_a.pk,
        "translation": "salut",
        "value": ["salut"],
        "locale": locale_a.code,
    }
    form = CreateTranslationForm(data)
    assert form.is_valid()
    assert form.cleaned_data["stats"] == ""

    data["stats"] = "all"
    form = CreateTranslationForm(data)
    assert form.is_valid()
    assert form.cleaned_data["stats"] == "all"

    data["stats"] = "resource"
    form = CreateTranslationForm(data)
    assert form.is_valid()
    assert form.cleaned_data["stats"] == "resource"

    data["stats"] = "foo"
    form = CreateTranslationForm(data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_create_translation_form_clean_translation(entity_a, locale_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": " salut ",
            "value": [" salut "],
            "locale": locale_a.code,
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["translation"] == " salut "
    assert form.cleaned_data["value"] == [" salut "]
    assert form.cleaned_data["properties"] is None
