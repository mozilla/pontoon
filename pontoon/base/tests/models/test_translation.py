import pytest

from pontoon.base.models import (
    Entity,
    ProjectLocale,
    Resource,
    TranslatedResource,
    Translation,
    TranslationMemoryEntry,
)
from pontoon.base.tests import (
    LocaleFactory,
    ProjectFactory,
)
from pontoon.base.utils import aware_datetime


@pytest.fixture
def locale_a():
    return LocaleFactory(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def project_a():
    return ProjectFactory(
        slug="project_a", name="Project A", repositories=[],
    )


@pytest.mark.django_db
def test_translation_save_latest_update(locale_a, project_a):
    """
    When a translation is saved, update the latest_translation
    attribute on the related project, locale, translatedresource,
    and project_locale objects.
    """
    project_locale = ProjectLocale.objects.create(
        project=project_a, locale=locale_a,
    )
    resource = Resource.objects.create(
        project=project_a,
        path="resource.po",
        format="po",
    )
    tr = TranslatedResource.objects.create(locale=locale_a, resource=resource)
    entity = Entity.objects.create(resource=resource, string="Entity X")

    assert locale_a.latest_translation is None
    assert project_a.latest_translation is None
    assert tr.latest_translation is None
    assert project_locale.latest_translation is None

    translation = Translation.objects.create(
        locale=locale_a,
        entity=entity,
        date=aware_datetime(1970, 1, 1),
    )
    locale_a.refresh_from_db()
    project_a.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation
    assert project_locale.latest_translation == translation

    # Ensure translation is replaced for newer translations
    newer_translation = Translation.objects.create(
        locale=locale_a,
        entity=entity,
        date=aware_datetime(1970, 2, 1),
    )
    locale_a.refresh_from_db()
    project_a.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert locale_a.latest_translation == newer_translation
    assert project_a.latest_translation == newer_translation
    assert tr.latest_translation == newer_translation
    assert project_locale.latest_translation == newer_translation

    # Ensure translation isn't replaced for older translations.
    Translation.objects.create(
        locale=locale_a,
        entity=entity,
        date=aware_datetime(1970, 1, 5),
    )
    locale_a.refresh_from_db()
    project_a.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert locale_a.latest_translation == newer_translation
    assert project_a.latest_translation == newer_translation
    assert tr.latest_translation == newer_translation
    assert project_locale.latest_translation == newer_translation

    # Ensure approved_date is taken into consideration as well.
    newer_approved_translation = Translation.objects.create(
        locale=locale_a,
        entity=entity,
        approved_date=aware_datetime(1970, 3, 1),
    )
    locale_a.refresh_from_db()
    project_a.refresh_from_db()
    tr.refresh_from_db()
    project_locale.refresh_from_db()
    assert locale_a.latest_translation == newer_approved_translation
    assert project_a.latest_translation == newer_approved_translation
    assert tr.latest_translation == newer_approved_translation
    assert project_locale.latest_translation == newer_approved_translation


@pytest.mark.django_db
def test_translation_save_latest_missing_project_locale(locale_a, project_a):
    """
    If a translation is saved for a locale that isn't active on the
    project, do not fail due to a missing ProjectLocale.
    """
    resource = Resource.objects.create(
        project=project_a,
        path="resource.po",
        format="po",
    )
    tr = TranslatedResource.objects.create(locale=locale_a, resource=resource)
    entity = Entity.objects.create(resource=resource, string="Entity X")

    # This calls .save, this should fail if we're not properly
    # handling the missing ProjectLocale.
    translation = Translation.objects.create(
        locale=locale_a,
        entity=entity,
        date=aware_datetime(1970, 1, 1),
    )

    locale_a.refresh_from_db()
    project_a.refresh_from_db()
    tr.refresh_from_db()
    assert locale_a.latest_translation == translation
    assert project_a.latest_translation == translation
    assert tr.latest_translation == translation


@pytest.mark.django_db
def test_translation_approved_in_tm(locale_a, project_a):
    """
    Every save of approved translation should generate a new
    entry in the translation memory.
    """
    resource = Resource.objects.create(
        project=project_a,
        path="resource.po",
        format="po",
    )
    entity = Entity.objects.create(resource=resource, string="Entity X")
    translation = Translation.objects.create(
        locale=locale_a,
        entity=entity,
        approved=True,
    )
    assert TranslationMemoryEntry.objects.get(
        source=translation.entity.string,
        target=translation.string,
        locale=translation.locale,
    )


@pytest.mark.django_db
def test_translation_unapproved_not_in_tm(locale_a, project_a):
    """
    Unapproved translation shouldn't be in the translation memory.
    """
    resource = Resource.objects.create(
        project=project_a,
        path="resource.po",
        format="po",
    )
    entity = Entity.objects.create(resource=resource, string="Entity X")
    translation = Translation.objects.create(
        locale=locale_a,
        entity=entity,
    )
    with pytest.raises(TranslationMemoryEntry.DoesNotExist):
        TranslationMemoryEntry.objects.get(
            source=translation.entity.string,
            target=translation.string,
            locale=translation.locale,
        )


@pytest.mark.django_db
def test_translation_rejected_not_in_tm(locale_a, project_a):
    """
    When translation is deleted, its corresponding TranslationMemoryEntry
    needs to be deleted, too.
    """
    resource = Resource.objects.create(
        project=project_a,
        path="resource.po",
        format="po",
    )
    entity = Entity.objects.create(resource=resource, string="Entity X")
    translation = Translation.objects.create(
        locale=locale_a,
        entity=entity,
        rejected=True,
    )
    with pytest.raises(TranslationMemoryEntry.DoesNotExist):
        TranslationMemoryEntry.objects.get(
            source=translation.entity.string,
            target=translation.string,
            locale=translation.locale,
        )
