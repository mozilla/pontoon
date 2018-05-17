import factory
import pytest

from django.contrib.auth import get_user_model
from pontoon.base.models import (
    Entity,
    Group,
    Locale,
    Project,
    ProjectLocale,
    Resource,
    Translation,
)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()


@pytest.fixture
def fake_user():
    return UserFactory(
        username="fake_user",
        email="fake_user@example.org"
    )


@pytest.fixture
def locale():
    translators_group = Group.objects.create(
        name='Klingon translators',
    )
    managers_group = Group.objects.create(
        name='Klingon managers',
    )
    return Locale.objects.create(
        code="kg",
        name="Klingon",
        translators_group=translators_group,
        managers_group=managers_group,
    )


@pytest.fixture
def project():
    return Project.objects.create(
        slug="project", name="Project"
    )


@pytest.fixture
def project_locale(project, locale):
    pl = ProjectLocale.objects.create(project=project, locale=locale)
    # ProjectLocale doesn't work without at least one resource.
    Resource.objects.create(
        project=project,
        path='foo.lang',
        total_strings=1
    )
    return pl


@pytest.fixture
def resource(locale, project):
    return Resource.objects.create(
        project=project, path="resource.po", format="po"
    )


@pytest.fixture
def entity(resource):
    return Entity.objects.create(
        resource=resource, string="entity"
    )


@pytest.fixture
def translation(locale, entity, fake_user):
    """Translation 0"""
    return Translation.objects.create(entity=entity, locale=locale)


@pytest.mark.django_db
def test_signal_base_project_locale_modified(project_locale, translation):
    """
    If ProjectLocale is modified (like setting the
    latest_translation), has_changed should not be modified.
    """
    project_locale.project.has_changed = False
    project_locale.project.save()
    project_locale.project.refresh_from_db()

    assert not project_locale.project.has_changed

    project_locale.latest_translation = None
    project_locale.project.save()
    project_locale.project.refresh_from_db()

    assert not project_locale.project.has_changed
    assert project_locale.latest_translation is None

    project_locale.latest_translation = translation
    project_locale.save()
    project_locale.project.refresh_from_db()

    assert not project_locale.project.has_changed
