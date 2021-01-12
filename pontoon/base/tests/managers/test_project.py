import pytest
from pontoon.base.tests import ProjectFactory, ProjectLocaleFactory
from pontoon.base.models import Project, ProjectLocale


@pytest.fixture
def public_project():
    yield ProjectFactory.create(visibility=Project.Visibility.PUBLIC)


@pytest.fixture
def private_project():
    yield ProjectFactory.create()


@pytest.fixture
def public_project_locale():
    yield ProjectLocaleFactory.create(project__visibility=Project.Visibility.PUBLIC)


@pytest.fixture
def private_project_locale():
    yield ProjectLocaleFactory.create()


@pytest.mark.django_db
def test_project_visibility_filters_on_superuser(
    public_project, private_project, admin
):
    visible_projects = Project.objects.visible_for(admin).filter(
        pk__in=[public_project.pk, private_project.pk]
    )
    assert list(visible_projects) == [public_project, private_project]


@pytest.mark.django_db
def test_project_visibility_filters_on_contributors(
    public_project, private_project, user_a
):
    visible_projects = Project.objects.visible_for(user_a).filter(
        pk__in=[public_project.pk, private_project.pk]
    )
    assert list(visible_projects) == [public_project]


@pytest.mark.django_db
def test_project_locale_visibility_filters_on_superuser(
    public_project_locale, private_project_locale, admin
):
    visible_project_locales = ProjectLocale.objects.visible_for(admin).filter(
        pk__in=[public_project_locale.pk, private_project_locale.pk]
    )
    assert list(visible_project_locales) == [
        public_project_locale,
        private_project_locale,
    ]


@pytest.mark.django_db
def test_project_locale_visibility_filters_on_contributors(
    public_project_locale, private_project_locale, user_a
):
    visible_project_locales = ProjectLocale.objects.visible_for(user_a).filter(
        pk__in=[public_project_locale.pk, private_project_locale.pk]
    )
    assert list(visible_project_locales) == [public_project_locale]
