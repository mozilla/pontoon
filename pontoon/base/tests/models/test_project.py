import functools

from unittest.mock import patch

import pytest

from django.contrib.auth.models import AnonymousUser

from pontoon.base.models import Project, ProjectLocale
from pontoon.test.factories import LocaleFactory, ProjectFactory, ProjectLocaleFactory


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
