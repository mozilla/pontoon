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

    assert form.errors["plural_form"]
    assert form.errors["plural_form"][0] == "This field is required."

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
            "locale": locale_a.code,
            "plural_form": "-1",
            "original": "hello",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["entity"] == entity_a


@pytest.mark.django_db
def test_create_translation_form_clean_locale(entity_a, locale_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "locale": locale_a.code,
            "plural_form": "-1",
            "original": "hello",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["locale"] == locale_a


@pytest.mark.django_db
def test_create_translation_form_clean_plural_form(entity_a, locale_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "locale": locale_a.code,
            "plural_form": "-1",
            "original": "hello",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["plural_form"] is None

    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "locale": locale_a.code,
            "plural_form": "1",
            "original": "hello",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["plural_form"] == "1"


@pytest.mark.django_db
def test_create_translation_form_clean_paths(entity_a, locale_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "locale": locale_a.code,
            "plural_form": "-1",
            "original": "hello",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["paths"] == []

    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": "salut",
            "locale": locale_a.code,
            "plural_form": "-1",
            "original": "hello",
            "paths[]": ["a/d.ext", "foo/bar"],
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["paths"] == ["a/d.ext", "foo/bar"]


@pytest.mark.django_db
def test_create_translation_form_clean_translation(entity_a, locale_a):
    form = CreateTranslationForm(
        {
            "entity": entity_a.pk,
            "translation": " salut ",
            "locale": locale_a.code,
            "plural_form": "-1",
            "original": "hello",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["translation"] == " salut "
