
import pytest

from pontoon.base.models import (
    Entity, ProjectLocale, Resource, TranslatedResource,
    Translation, TranslationMemoryEntry)
from pontoon.base.utils import aware_datetime


@pytest.mark.django_db
def test_translation_save_latest_update(localeX, projectX):
    """
    When a translation is saved, update the latest_translation
    attribute on the related project, locale, translatedresource,
    and project_locale objects.
    """
    project_locale = ProjectLocale.objects.create(
        project=projectX, locale=localeX)
    resource = Resource.objects.create(
        project=projectX,
        path="resource.po",
        format="po")
    tr = TranslatedResource.objects.create(
        locale=localeX, resource=resource)
    entity = Entity.objects.create(
        resource=resource, string="Entity X")

    assert localeX.latest_translation is None
    assert projectX.latest_translation is None
    assert tr.latest_translation is None
    assert project_locale.latest_translation is None

    translation = Translation.objects.create(
        locale=localeX,
        entity=entity,
        date=aware_datetime(1970, 1, 1))
    localeX.refresh_from_db()
    projectX.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert localeX.latest_translation == translation
    assert projectX.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale.latest_translation == translation

    # Ensure translation is replaced for newer translations
    newer_translation = Translation.objects.create(
        locale=localeX,
        entity=entity,
        date=aware_datetime(1970, 2, 1))
    localeX.refresh_from_db()
    projectX.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert localeX.latest_translation == newer_translation
    assert projectX.latest_translation == newer_translation
    assert tr.latest_translation == newer_translation
    assert project_locale.latest_translation == newer_translation

    # Ensure translation isn't replaced for older translations.
    Translation.objects.create(
        locale=localeX,
        entity=entity,
        date=aware_datetime(1970, 1, 5))
    localeX.refresh_from_db()
    projectX.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert localeX.latest_translation == newer_translation
    assert projectX.latest_translation == newer_translation
    assert tr.latest_translation == newer_translation
    assert project_locale.latest_translation == newer_translation

    # Ensure approved_date is taken into consideration as well.
    newer_approved_translation = Translation.objects.create(
        locale=localeX,
        entity=entity,
        approved_date=aware_datetime(1970, 3, 1))
    localeX.refresh_from_db()
    projectX.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert localeX.latest_translation == newer_approved_translation
    assert projectX.latest_translation == newer_approved_translation
    assert tr.latest_translation == newer_approved_translation
    assert project_locale.latest_translation == newer_approved_translation


@pytest.mark.django_db
def test_translation_save_latest_missing_project_locale(localeX, projectX):
    """
    If a translation is saved for a locale that isn't active on the
    project, do not fail due to a missing ProjectLocale.
    """
    resource = Resource.objects.create(
        project=projectX,
        path="resource.po",
        format="po")
    tr = TranslatedResource.objects.create(
        locale=localeX, resource=resource)
    entity = Entity.objects.create(
        resource=resource, string="Entity X")

    # This calls .save, this should fail if we're not properly
    # handling the missing ProjectLocale.
    translation = Translation.objects.create(
        locale=localeX,
        entity=entity,
        date=aware_datetime(1970, 1, 1))

    localeX.refresh_from_db()
    projectX.refresh_from_db()
    tr.refresh_from_db()
    assert localeX.latest_translation == translation
    assert projectX.latest_translation == translation
    assert tr.latest_translation == translation


@pytest.mark.django_db
def test_translation_approved_in_tm(localeX, projectX):
    """
    Every save of approved translation should generate a new
    entry in the translation memory.
    """
    resource = Resource.objects.create(
        project=projectX,
        path="resource.po",
        format="po")
    entity = Entity.objects.create(
        resource=resource, string="Entity X")
    translation = Translation.objects.create(
        locale=localeX,
        entity=entity,
        approved=True)
    assert TranslationMemoryEntry.objects.get(
        source=translation.entity.string,
        target=translation.string,
        locale=translation.locale)


@pytest.mark.django_db
def test_translation_unapproved_not_in_tm(localeX, projectX):
    """
    Unapproved translation shouldn't be in the translation memory.
    """
    resource = Resource.objects.create(
        project=projectX,
        path="resource.po",
        format="po")
    entity = Entity.objects.create(
        resource=resource, string="Entity X")
    translation = Translation.objects.create(
        locale=localeX,
        entity=entity)
    with pytest.raises(TranslationMemoryEntry.DoesNotExist):
        TranslationMemoryEntry.objects.get(
            source=translation.entity.string,
            target=translation.string,
            locale=translation.locale)


@pytest.mark.django_db
def test_translation_rejected_not_in_tm(localeX, projectX):
    """
    When translation is deleted, its corresponding TranslationMemoryEntry
    needs to be deleted, too.
    """
    resource = Resource.objects.create(
        project=projectX,
        path="resource.po",
        format="po")
    entity = Entity.objects.create(
        resource=resource, string="Entity X")
    translation = Translation.objects.create(
        locale=localeX,
        entity=entity,
        rejected=True)
    with pytest.raises(TranslationMemoryEntry.DoesNotExist):
        TranslationMemoryEntry.objects.get(
            source=translation.entity.string,
            target=translation.string,
            locale=translation.locale)
