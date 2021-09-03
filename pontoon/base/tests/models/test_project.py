import functools
import os
from unittest.mock import patch

import pytest
from django.contrib.auth.models import AnonymousUser

from pontoon.base.models import ProjectLocale, Project, Repository
from pontoon.test.factories import (
    ChangedEntityLocaleFactory,
    EntityFactory,
    ProjectLocaleFactory,
    RepositoryFactory,
    ResourceFactory,
    ProjectFactory,
    LocaleFactory,
)


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
    assert project_a.repositories.first().type == Repository.Type.GIT
    assert project_a.repository_type == Repository.Type.GIT


@pytest.mark.django_db
def test_project_repo_path_none(project_a):
    """
    If the project has no matching repositories, raise a ValueError.
    """
    with pytest.raises(ValueError):
        project_a.repository_for_path("doesnt/exist")


@pytest.mark.django_db
def test_project_repo_for_path(project_a):
    """
    Return the first repo found with a checkout path that contains
    the given path.
    """
    repos = [
        RepositoryFactory.create(type="file", project=project_a, url="testrepo%s" % i,)
        for i in range(0, 3)
    ]
    path = os.path.join(repos[1].checkout_path, "foo", "bar")
    assert project_a.repository_for_path(path) == repos[1]


@pytest.mark.django_db
def test_project_needs_sync(project_a, project_b, locale_a):
    """
    Project.needs_sync should be True if ChangedEntityLocale objects
    exist for its entities or if Project has unsynced locales.
    """
    resource = ResourceFactory.create(project=project_a, path="resourceX.po")
    entity = EntityFactory.create(resource=resource, string="entityX")

    assert not project_a.needs_sync
    ChangedEntityLocaleFactory.create(entity=entity, locale=locale_a)
    assert project_a.needs_sync

    assert not project_b.needs_sync
    assert project_b.unsynced_locales == []
    del project_b.unsynced_locales
    ProjectLocaleFactory.create(
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
    assert project_a.get_latest_activity() == translation_a.latest_activity


@pytest.mark.django_db
def test_project_latest_activity_without_latest(project_a):
    assert project_a.latest_translation is None
    assert project_a.get_latest_activity() is None


@pytest.mark.django_db
def test_project_latest_activity_with_locale(locale_a, project_a):
    with patch.object(ProjectLocale, "get_latest_activity") as m:
        m.return_value = "latest"
        assert project_a.get_latest_activity(locale=locale_a) == "latest"
        assert m.call_args[0] == (project_a, locale_a)


@pytest.fixture
def public_project():
    yield ProjectFactory.create()


@pytest.fixture
def private_project():
    yield ProjectFactory.create(visibility=Project.Visibility.PRIVATE)


@pytest.mark.parametrize(
    "users_permissions_group",
    (
        # Check visibility of projects for a project translator
        "translators_group",
        # Check visibility of projects for a locale translator
        "locale.translators_group",
        # Check visibility of projects for a locale manager
        "locale.managers_group",
    ),
)
@pytest.mark.django_db
def test_project_visible_for_users(
    users_permissions_group, user_a, public_project, private_project
):
    def get_permissions_group(obj, permissions_group):
        def _getattr(obj, permissions_group):
            return getattr(obj, permissions_group)

        return functools.reduce(_getattr, [obj] + permissions_group.split("."))

    projects = Project.objects.visible_for(user_a).filter(
        pk__in=[public_project.pk, private_project.pk]
    )
    assert list(projects) == [
        public_project,
    ]

    # Make user_a a project translator
    private_project_locale = ProjectLocaleFactory.create(
        project=private_project, locale=LocaleFactory.create()
    )
    get_permissions_group(private_project_locale, users_permissions_group).user_set.add(
        user_a
    )

    projects = Project.objects.visible_for(user_a).filter(
        pk__in=[public_project.pk, private_project.pk]
    )
    assert list(projects) == [public_project]


@pytest.mark.django_db
def test_project_visible_for_superuser(admin, public_project, private_project):
    assert list(
        Project.objects.visible_for(admin).filter(
            pk__in=[public_project.pk, private_project.pk]
        )
    ) == [public_project, private_project]


@pytest.mark.django_db
def test_project_visible_for_anonymous(public_project, private_project):
    assert list(
        Project.objects.visible_for(AnonymousUser()).filter(
            pk__in=[public_project.pk, private_project.pk]
        )
    ) == [public_project]
