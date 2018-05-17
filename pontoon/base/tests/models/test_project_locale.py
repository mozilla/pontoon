import pytest

from pontoon.base.models import ProjectLocale

from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
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
def translation_a(locale_a, project_a, entity_a, user_a):
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
    return TranslationFactory(
        entity=entity_a, locale=locale_a, user=user_a
    )


@pytest.mark.django_db
def test_projectlocale_latest_activity_doesnt_exist(project_a, locale_a):
    """
    If no ProjectLocale exists with the given project/locale,
    return None.
    """
    assert not (
        ProjectLocale.objects
        .filter(project=project_a, locale=locale_a)
        .exists()
    )
    assert ProjectLocale.get_latest_activity(project_a, locale_a) is None


@pytest.mark.django_db
def test_projectlocale_latest_activity_no_latest(project_a, locale_a):
    """
    If the matching ProjectLocale has no latest_translation, return
    None.
    """
    ProjectLocale.objects.create(project=project_a, locale=locale_a)
    assert ProjectLocale.get_latest_activity(project_a, locale_a) is None


@pytest.mark.django_db
def test_projectlocale_latest_activity_success(translation_a):
    """
    If the matching ProjectLocale has a latest_translation, return
    it's latest_activity.
    """
    project = translation_a.entity.resource.project
    locale = translation_a.locale
    assert ProjectLocale.get_latest_activity(project, locale)
    assert (
        ProjectLocale.get_latest_activity(project, locale)
        == translation_a.latest_activity
    )


@pytest.mark.django_db
def test_projectlocale_translators_group(project_a, locale_a, user_a):
    """
    Tests if user has permission to translate project at specific
    locale after assigment.
    """
    project_locale = ProjectLocale.objects.create(
        project=project_a,
        locale=locale_a,
        has_custom_translators=True,
    )

    assert user_a.can_translate(locale=locale_a, project=project_a) is False

    user_a.groups.add(project_locale.translators_group)
    assert user_a.can_translate(locale=locale_a, project=project_a) is True

    project_locale.has_custom_translators = False
    project_locale.save()
    assert user_a.can_translate(locale=locale_a, project=project_a) is False
