from unittest.mock import patch, call

import pytest

from pontoon.base.models import Project, TranslationMemoryEntry
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)
from pontoon.base.utils import aware_datetime


@pytest.mark.django_db
def test_translation_save_latest_update_first_translation(
    locale_a, project_a, project_locale_a, resource_a, entity_a
):
    """
    When a translation is saved, update the latest_translation
    attribute on the related project, locale, translatedresource,
    and project_locale objects.
    """
    tr = TranslatedResourceFactory.create(locale=locale_a, resource=resource_a)

    assert locale_a.latest_translation is None
    assert project_a.latest_translation is None
    assert tr.latest_translation is None
    assert project_locale_a.latest_translation is None

    translation = TranslationFactory.create(
        locale=locale_a, entity=entity_a, date=aware_datetime(1970, 1, 1),
    )
    for i in [locale_a, project_a, project_locale_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale_a.latest_translation == translation


@pytest.mark.django_db
def test_translation_save_latest_update_newer_translation(
    locale_a, project_a, project_locale_a, resource_a, entity_a
):
    """
    When a newer translation is saved, update the latest_translation
    attribute on the related project, locale, translatedresource,
    and project_locale objects.
    """
    tr = TranslatedResourceFactory.create(locale=locale_a, resource=resource_a)

    translation = TranslationFactory.create(
        locale=locale_a, entity=entity_a, date=aware_datetime(1970, 1, 1),
    )
    for i in [locale_a, project_a, project_locale_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale_a.latest_translation == translation

    newer_translation = TranslationFactory.create(
        locale=locale_a, entity=entity_a, date=aware_datetime(1970, 2, 1),
    )
    for i in [locale_a, project_a, project_locale_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == newer_translation
    assert project_a.latest_translation == newer_translation
    assert tr.latest_translation == newer_translation
    assert project_locale_a.latest_translation == newer_translation


@pytest.mark.django_db
def test_translation_save_latest_update_older_translation(
    locale_a, project_a, project_locale_a, resource_a, entity_a
):
    """
    When an older translation is saved, do not update the latest_translation
    attribute on the related project, locale, translatedresource,
    and project_locale objects.
    """
    tr = TranslatedResourceFactory.create(locale=locale_a, resource=resource_a)

    translation = TranslationFactory.create(
        locale=locale_a, entity=entity_a, date=aware_datetime(1970, 2, 1),
    )
    for i in [locale_a, project_a, project_locale_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale_a.latest_translation == translation

    # older translation
    TranslationFactory.create(
        locale=locale_a, entity=entity_a, date=aware_datetime(1970, 1, 1),
    )
    for i in [locale_a, project_a, project_locale_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale_a.latest_translation == translation


@pytest.mark.django_db
def test_translation_save_latest_update_approved_translation(
    locale_a, project_a, project_locale_a, resource_a, entity_a
):
    """
    When a translation is approved, update the latest_translation
    attribute on the related project, locale, translatedresource,
    and project_locale objects if it was approved later than the last
    translation was saved before.
    """
    tr = TranslatedResourceFactory.create(locale=locale_a, resource=resource_a)

    translation = TranslationFactory.create(
        locale=locale_a,
        entity=entity_a,
        date=aware_datetime(1970, 2, 1),
        approved_date=aware_datetime(1970, 2, 1),
    )
    for i in [locale_a, project_a, project_locale_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale_a.latest_translation == translation

    later_approved_translation = TranslationFactory.create(
        locale=locale_a,
        entity=entity_a,
        date=aware_datetime(1970, 1, 1),
        approved_date=aware_datetime(1970, 3, 1),
    )
    for i in [locale_a, project_a, project_locale_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == later_approved_translation
    assert project_a.latest_translation == later_approved_translation
    assert tr.latest_translation == later_approved_translation
    assert project_locale_a.latest_translation == later_approved_translation


@pytest.mark.django_db
def test_translation_save_latest_update_for_system_project(locale_a, system_project_a):
    """
    When a translation is saved for a system project, update the latest_translation
    attribute on the project, translatedresource and project_locale objects,
    but not on the locale object.
    """
    project_locale = ProjectLocaleFactory.create(
        project=system_project_a, locale=locale_a,
    )
    resource = ResourceFactory.create(
        project=system_project_a, path="resource.po", format="po",
    )
    tr = TranslatedResourceFactory.create(locale=locale_a, resource=resource)
    entity = EntityFactory.create(resource=resource, string="Entity X")

    assert locale_a.latest_translation is None
    assert system_project_a.latest_translation is None
    assert tr.latest_translation is None
    assert project_locale.latest_translation is None

    translation = TranslationFactory.create(
        locale=locale_a, entity=entity, date=aware_datetime(1970, 1, 1),
    )
    for i in [locale_a, system_project_a, project_locale, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation is None
    assert system_project_a.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale.latest_translation == translation


@pytest.mark.django_db
def test_translation_save_latest_missing_project_locale(
    locale_a, project_a, resource_a, entity_a
):
    """
    If a translation is saved for a locale that isn't active on the
    project, do not fail due to a missing ProjectLocale.
    """
    tr = TranslatedResourceFactory.create(locale=locale_a, resource=resource_a)

    # This calls .save, this should fail if we're not properly
    # handling the missing ProjectLocale.
    translation = TranslationFactory.create(
        locale=locale_a, entity=entity_a, date=aware_datetime(1970, 1, 1),
    )

    for i in [locale_a, project_a, tr]:
        i.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation


@pytest.mark.django_db
def test_translation_approved_in_tm(locale_a, entity_a):
    """
    Every save of approved translation should generate a new
    entry in the translation memory.
    """
    translation = TranslationFactory.create(
        locale=locale_a, entity=entity_a, approved=True,
    )
    assert TranslationMemoryEntry.objects.get(
        source=translation.entity.string,
        target=translation.string,
        locale=translation.locale,
    )


@pytest.mark.django_db
def test_translation_unapproved_not_in_tm(locale_a, entity_a):
    """
    Unapproved translation shouldn't be in the translation memory.
    """
    translation = TranslationFactory.create(locale=locale_a, entity=entity_a,)
    with pytest.raises(TranslationMemoryEntry.DoesNotExist):
        TranslationMemoryEntry.objects.get(
            source=translation.entity.string,
            target=translation.string,
            locale=translation.locale,
        )


@pytest.mark.django_db
def test_translation_rejected_not_in_tm(locale_a, entity_a):
    """
    When translation is deleted, its corresponding TranslationMemoryEntry
    needs to be deleted, too.
    """
    translation = TranslationFactory.create(
        locale=locale_a, entity=entity_a, rejected=True,
    )
    with pytest.raises(TranslationMemoryEntry.DoesNotExist):
        TranslationMemoryEntry.objects.get(
            source=translation.entity.string,
            target=translation.string,
            locale=translation.locale,
        )


@pytest.mark.django_db
@patch("pontoon.base.models.Entity.reset_term_translation")
def test_translation_in_terminology_saved(reset_term_translation_mock, locale_a):
    """
    When translation in the "Terminology" project gets saved,
    call the reset_term_translation() method.
    """
    project, _ = Project.objects.get_or_create(slug="terminology")
    entity = EntityFactory.create(resource=project.resources.first())
    TranslationFactory.create(locale=locale_a, entity=entity)

    assert reset_term_translation_mock.called
    assert reset_term_translation_mock.call_args == call(locale_a)


@pytest.mark.django_db
@patch("pontoon.base.models.Entity.reset_term_translation")
def test_translation_not_in_terminology_saved(
    reset_term_translation_mock, locale_a, entity_a
):
    """
    When translation not in the "Terminology" project gets saved,
    do not call the reset_term_translation() method.
    """
    TranslationFactory.create(locale=locale_a, entity=entity_a)

    assert not reset_term_translation_mock.called
