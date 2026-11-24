"""
Test consistency of calculations between `calculate_stats` and `translation.save()`.
"""

import pytest

from pontoon.base.models import Project, TranslatedResource
from pontoon.test.factories import TranslatedResourceFactory, TranslationFactory


def get_stats(translation):
    return TranslatedResource.objects.filter(
        resource=translation.entity.resource,
        locale=translation.locale,
    ).string_stats()


@pytest.mark.django_db
def test_translation_approved(translation_a):
    translation_a.approved = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 1,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }

    translation_a.approved = False
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }


@pytest.mark.django_db
def test_translation_pretranslated(translation_a):
    translation_a.pretranslated = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 1,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }

    translation_a.pretranslated = False
    translation_a.rejected = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }


@pytest.mark.django_db
def test_translation_with_error(translation_a):
    translation_a.approved = True
    translation_a.save(failed_checks={"pErrors": ["error"]})

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 1,
    }

    translation_a.approved = False
    translation_a.pretranslated = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 1,
    }

    translation_a.pretranslated = False
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }


@pytest.mark.django_db
def test_approve_with_competing_translations(translation_a):
    """
    Approving one translation must reject all other unreviewed translations
    for the same entity+locale and leave stats consistent.
    """
    translation_b = TranslationFactory(
        entity=translation_a.entity,
        locale=translation_a.locale,
    )

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 2,
        "warnings": 0,
        "errors": 0,
    }

    translation_a.approved = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 1,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }

    translation_b.refresh_from_db()
    assert translation_b.rejected


@pytest.mark.django_db
def test_translation_with_warning(translation_a):
    translation_a.approved = True
    translation_a.save(failed_checks={"pWarnings": ["warning"]})

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 1,
        "errors": 0,
    }

    translation_a.approved = False
    translation_a.pretranslated = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 1,
        "errors": 0,
    }

    translation_a.pretranslated = False
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }


@pytest.mark.django_db
def test_string_stats_includes_private_projects(project_a, locale_a, resource_a):
    """Private projects are included unless only_public is requested."""
    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=2, approved_strings=1
    )

    query = TranslatedResource.objects.filter(resource__project=project_a)
    assert query.string_stats()["total"] == 2
    assert query.string_stats()["approved"] == 1
    assert query.string_stats(only_public=True)["total"] == 0


@pytest.mark.django_db
def test_query_stats_includes_private_project(project_a, locale_a, resource_a):
    """query_stats includes stats for a private project."""
    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=2, approved_strings=1
    )

    stats = TranslatedResource.objects.query_stats(project_a, [], locale_a)
    assert stats["total"] == 2
    assert stats["approved"] == 1


@pytest.mark.django_db
def test_query_stats_all_projects_excludes_private(
    project_a, project_b, locale_a, resource_a, resource_b
):
    """All-projects query_stats keeps excluding private projects."""
    project_b.visibility = Project.Visibility.PRIVATE
    project_b.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=3, approved_strings=2
    )
    TranslatedResourceFactory.create(
        resource=resource_b, locale=locale_a, total_strings=4, approved_strings=1
    )

    stats = TranslatedResource.objects.query_stats(
        Project(slug="all-projects"), [], locale_a
    )
    assert stats["total"] == 3
    assert stats["approved"] == 2


@pytest.mark.django_db
def test_aggregated_stats_includes_private_project(project_a, locale_a, resource_a):
    """Project stats include strings from private projects."""
    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=2, approved_strings=1
    )

    assert project_a.total_strings == 2
    assert project_a.approved_strings == 1


@pytest.mark.django_db
def test_aggregated_stats_includes_private_project_locale(
    project_a, locale_a, project_locale_a, resource_a
):
    """ProjectLocale stats include strings from private projects."""
    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=2, approved_strings=1
    )

    assert project_locale_a.total_strings == 2
    assert project_locale_a.approved_strings == 1


@pytest.mark.django_db
def test_locale_aggregated_stats_excludes_private_projects(
    project_a, project_b, locale_a, resource_a, resource_b
):
    """Locale stats only aggregate public projects."""
    project_b.visibility = Project.Visibility.PRIVATE
    project_b.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=3, approved_strings=2
    )
    TranslatedResourceFactory.create(
        resource=resource_b, locale=locale_a, total_strings=4, approved_strings=1
    )

    assert locale_a.total_strings == 3
    assert locale_a.approved_strings == 2
