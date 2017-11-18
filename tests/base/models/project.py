
import os

import pytest

from mock import patch

from pontoon.base.models import (
    ChangedEntityLocale, ProjectLocale, Repository)


@pytest.mark.django_db
def test_project_commit_no_repos(project0):
    """can_commit should be False if there are no repos."""

    assert project0.repositories.count() is 0
    assert not project0.can_commit


@pytest.mark.django_db
def test_project_commit_false(project0, repo_file0):
    """
    can_commit should be False if there are no repo xthat can be
    committed to.
    """
    assert project0.repositories.first().type == "file"
    assert not project0.can_commit


@pytest.mark.django_db
def test_project_commit_true(project0, repo_git0):
    """
    can_commit should be True if there is a repo that can be
    committed to.
    """
    assert project0.repositories.first().type == "git"
    assert project0.can_commit


@pytest.mark.django_db
def test_project_type_no_repos(project0):
    """If a project has no repos, repository_type should be None."""
    assert project0.repository_type is None


@pytest.mark.django_db
def test_project_type_multi_repos(project0, repo_git0, repo_hg0):
    """
    If a project has repos, return the type of the repo created
    first.
    """
    assert project0.repositories.first().type == "git"
    assert project0.repository_type == "git"


@pytest.mark.django_db
def test_project_repo_path_none(project0):
    """
    If the project has no matching repositories, raise a ValueError.
    """
    with pytest.raises(ValueError):
        project0.repository_for_path('doesnt/exist')


@pytest.mark.django_db
def test_project_repo_for_path(project0):
    """
    Return the first repo found with a checkout path that contains
    the given path.
    """
    repos = [
        Repository.objects.create(
            type="file",
            project=project0,
            url="testrepo%s" % i)
        for i in range(0, 3)]
    path = os.path.join(repos[1].checkout_path, 'foo', 'bar')
    assert project0.repository_for_path(path) == repos[1]


@pytest.mark.django_db
def test_project_needs_sync(project0, project1, entity0, locale0):
    """
    Project.needs_sync should be True if ChangedEntityLocale objects
    exist for its entities or if Project has unsynced locales.
    """
    # False ?
    assert project0.needs_sync == []
    ChangedEntityLocale.objects.create(entity=entity0, locale=locale0)
    assert project0.needs_sync is True

    assert project1.needs_sync == []
    assert project1.unsynced_locales == []
    del project1.unsynced_locales
    ProjectLocale.objects.create(
        project=project1, locale=locale0)
    assert project1.needs_sync == [locale0]


@pytest.mark.django_db
def test_project_latest_activity_with_latest(project0, translation0):
    """
    If the project has a latest_translation and no locale is given,
    return it.
    """
    assert project0.latest_translation == translation0
    assert (
        project0.get_latest_activity()
        == translation0.latest_activity)


@pytest.mark.django_db
def test_project_latest_activity_without_latest(projectX):
    assert projectX.latest_translation is None
    assert projectX.get_latest_activity() is None


@pytest.mark.django_db
def test_project_latest_activity_with_locale(locale0, project0):

    with patch.object(ProjectLocale, 'get_latest_activity') as m:
        m.return_value = 'latest'
        assert project0.get_latest_activity(locale=locale0) == 'latest'
        assert m.call_args[0] == (project0, locale0)
