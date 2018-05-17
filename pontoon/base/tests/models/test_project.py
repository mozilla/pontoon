import os

import pytest

from mock import patch

from pontoon.base.models import (
    ChangedEntityLocale, Entity, ProjectLocale, Resource, Repository
)
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
)


@pytest.fixture
def user_a():
    return UserFactory(
        username="user_a",
        email="user_a@example.org"
    )


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


@pytest.fixture
def project_b():
    return ProjectFactory(
        slug="project_b", name="Project B"
    )


@pytest.fixture
def resource_a(locale_a, project_a):
    return ResourceFactory(
        project=project_a, path="resource_a.po", format="po"
    )


@pytest.fixture
def entity_a(resource_a):
    return EntityFactory(
        resource=resource_a, string="entity"
    )


@pytest.fixture
def translation_a(locale_a, entity_a, user_a):
    return TranslationFactory(
        entity=entity_a, locale=locale_a, user=user_a
    )


@pytest.fixture
def repo_file(project_a):
    """Repo (file) 0"""
    return Repository.objects.create(
        type="file", project=project_a, url="repo_file0",
    )


@pytest.fixture
def repo_git(project_a):
    """Repo (git) 0"""
    return Repository.objects.create(
        type="git", project=project_a, url="repo_git0",
    )


@pytest.fixture
def repo_hg(project_a):
    """Repo (hg) 0"""
    return Repository.objects.create(
        type="hg", project=project_a, url="repo_hg0",
    )


@pytest.mark.django_db
def test_project_commit_no_repos(project_a):
    """can_commit should be False if there are no repos."""

    assert project_a.repositories.count() == 0
    assert not project_a.can_commit


@pytest.mark.django_db
def test_project_commit_false(project_a, repo_file):
    """
    can_commit should be False if there are no repo xthat can be
    committed to.
    """
    assert project_a.repositories.first().type == "file"
    assert not project_a.can_commit


@pytest.mark.django_db
def test_project_commit_true(project_a, repo_git):
    """
    can_commit should be True if there is a repo that can be
    committed to.
    """
    assert project_a.repositories.first().type == "git"
    assert project_a.can_commit


@pytest.mark.django_db
def test_project_type_no_repos(project_a):
    """If a project has no repos, repository_type should be None."""
    assert project_a.repository_type is None


@pytest.mark.django_db
def test_project_type_multi_repos(project_a, repo_git, repo_hg):
    """
    If a project has repos, return the type of the repo created
    first.
    """
    assert project_a.repositories.first().type == "git"
    assert project_a.repository_type == "git"


@pytest.mark.django_db
def test_project_repo_path_none(project_a):
    """
    If the project has no matching repositories, raise a ValueError.
    """
    with pytest.raises(ValueError):
        project_a.repository_for_path('doesnt/exist')


@pytest.mark.django_db
def test_project_repo_for_path(project_a):
    """
    Return the first repo found with a checkout path that contains
    the given path.
    """
    repos = [
        Repository.objects.create(
            type="file",
            project=project_a,
            url="testrepo%s" % i,
        )
        for i in range(0, 3)
    ]
    path = os.path.join(repos[1].checkout_path, 'foo', 'bar')
    assert project_a.repository_for_path(path) == repos[1]


@pytest.mark.django_db
def test_project_needs_sync(project_a, project_b, locale_a):
    """
    Project.needs_sync should be True if ChangedEntityLocale objects
    exist for its entities or if Project has unsynced locales.
    """
    resource = Resource.objects.create(project=project_a, path="resourceX.po")
    entity = Entity.objects.create(resource=resource, string="entityX")

    assert not project_a.needs_sync
    ChangedEntityLocale.objects.create(entity=entity, locale=locale_a)
    assert project_a.needs_sync

    assert not project_b.needs_sync
    assert project_b.unsynced_locales == []
    del project_b.unsynced_locales
    ProjectLocale.objects.create(
        project=project_b, locale=locale_a,
    )
    assert project_b.needs_sync == [locale_a]


@pytest.mark.django_db
def test_project_latest_activity_with_latest(project_a, translation_a):
    """
    If the project has a latest_translation and no locale is given,
    return it.
    """
    assert project_a.latest_translation == translation_a
    assert (
        project_a.get_latest_activity()
        == translation_a.latest_activity
    )


@pytest.mark.django_db
def test_project_latest_activity_without_latest(project_a):
    assert project_a.latest_translation is None
    assert project_a.get_latest_activity() is None


@pytest.mark.django_db
def test_project_latest_activity_with_locale(locale_a, project_a):
    with patch.object(ProjectLocale, 'get_latest_activity') as m:
        m.return_value = 'latest'
        assert project_a.get_latest_activity(locale=locale_a) == 'latest'
        assert m.call_args[0] == (project_a, locale_a)
