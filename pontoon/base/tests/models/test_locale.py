import pytest

from mock import patch

from pontoon.base.models import (
    Entity, ProjectLocale, Resource, Subpage, TranslatedResource
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
def user_b():
    return UserFactory(
        username="user_b",
        email="user_b@example.org"
    )


@pytest.fixture
def locale_a():
    return LocaleFactory(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def locale_b():
    return LocaleFactory(
        code="gs",
        name="Geonosian",
    )


@pytest.fixture
def locale_c():
    return LocaleFactory(
        code="nv",
        name="Na'vi",
    )


@pytest.fixture
def project_a():
    return ProjectFactory(
        slug="project_a", name="Project A"
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
def resource_b(locale_b, project_b):
    return ResourceFactory(
        project=project_b, path="resource_b.po", format="po"
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
def locale_parts(project_b, locale_c, locale_b):
    ProjectLocale.objects.create(project=project_b, locale=locale_c)
    ProjectLocale.objects.create(project=project_b, locale=locale_b)
    resourceX = Resource.objects.create(
        project=project_b, path="resourceX.po", format="po",
    )
    entityX = Entity.objects.create(resource=resourceX, string="entityX")
    resourceX.total_strings = 1
    resourceX.save()
    TranslatedResource.objects.create(locale=locale_c, resource=resourceX)
    return locale_c, locale_b, entityX


@pytest.mark.django_db
def test_locale_latest_activity_with_latest(translation_a):
    """
    If the locale has a latest_translation and no project is given,
    return it.
    """
    locale = translation_a.locale
    assert (
        locale.get_latest_activity()
        == translation_a.latest_activity
    )


@pytest.mark.django_db
def test_locale_latest_activity_without_latest(locale_b):
    """
    If the locale doesn't have a latest_translation and no project
    is given, return None.
    """
    assert locale_b.get_latest_activity() is None


@pytest.mark.django_db
def test_locale_latest_activity_with_project(locale_a, project_a):
    """
    If a locale is given, defer to
    ProjectLocale.get_latest_activity.
    """
    with patch.object(ProjectLocale, 'get_latest_activity') as m:
        m.return_value = 'latest'
        assert locale_a.get_latest_activity(project=project_a) == 'latest'
        assert m.call_args[0] == (locale_a, project_a)


@pytest.mark.django_db
def test_locale_translators_group(locale_a, locale_b, user_a):
    """
    Tests if user has permission to translate locales after assigment.
    """
    assert user_a.has_perm('base.can_translate_locale') is False
    assert user_a.has_perm('base.can_translate_locale', locale_a) is False
    assert user_a.has_perm('base.can_translate_locale', locale_b) is False

    user_a.groups.add(locale_b.translators_group)
    assert user_a.has_perm('base.can_translate_locale') is False
    assert user_a.has_perm('base.can_translate_locale', locale_a) is False
    assert user_a.has_perm('base.can_translate_locale', locale_b) is True

    user_a.groups.add(locale_a.translators_group)
    assert user_a.has_perm('base.can_translate_locale') is False
    assert user_a.has_perm('base.can_translate_locale', locale_a) is True
    assert user_a.has_perm('base.can_translate_locale', locale_b) is True


@pytest.mark.django_db
def test_locale_managers_group(locale_a, locale_b, user_a):
    """
    Tests if user has permission to manage and translate locales after
    assigment.
    """
    assert user_a.has_perm('base.can_translate_locale') is False
    assert user_a.has_perm('base.can_translate_locale', locale_a) is False
    assert user_a.has_perm('base.can_translate_locale', locale_b) is False
    assert user_a.has_perm('base.can_manage_locale') is False
    assert user_a.has_perm('base.can_manage_locale', locale_a) is False
    assert user_a.has_perm('base.can_manage_locale', locale_b) is False

    user_a.groups.add(locale_b.managers_group)
    assert user_a.has_perm('base.can_translate_locale') is False
    assert user_a.has_perm('base.can_translate_locale', locale_a) is False
    assert user_a.has_perm('base.can_translate_locale', locale_b) is True
    assert user_a.has_perm('base.can_manage_locale') is False
    assert user_a.has_perm('base.can_manage_locale', locale_a) is False
    assert user_a.has_perm('base.can_manage_locale', locale_b) is True

    user_a.groups.add(locale_a.managers_group)
    assert user_a.has_perm('base.can_translate_locale') is False
    assert user_a.has_perm('base.can_translate_locale', locale_a) is True
    assert user_a.has_perm('base.can_translate_locale', locale_b) is True
    assert user_a.has_perm('base.can_manage_locale') is False
    assert user_a.has_perm('base.can_manage_locale', locale_a) is True
    assert user_a.has_perm('base.can_manage_locale', locale_b) is True


@pytest.mark.django_db
def test_locale_parts_stats_no_page_one_resource(locale_parts):
    """
    Return resource paths and stats if no subpage and one resource defined.
    """
    locale_c, locale_b, entityX = locale_parts
    project = entityX.resource.project
    details = locale_c.parts_stats(project)
    assert len(details) == 2
    assert details[0]['title'] == entityX.resource.path
    assert details[0]['translated_strings'] == 0


@pytest.mark.django_db
def test_locale_parts_stats_no_page_multiple_resources(locale_parts):
    """
    Return resource paths and stats for locales resources are available for.
    """
    locale_c, locale_b, entityX = locale_parts
    project = entityX.resource.project
    resourceY = Resource.objects.create(
        total_strings=1,
        project=project,
        path='/other/path.po',
    )
    Entity.objects.create(resource=resourceY, string="Entity Y")
    TranslatedResource.objects.create(
        resource=resourceY, locale=locale_c,
    )
    TranslatedResource.objects.create(
        resource=resourceY, locale=locale_b,
    )

    # results are sorted by title

    detailsX = locale_c.parts_stats(project)
    assert (
        [detail["title"] for detail in detailsX][:2]
        == sorted([entityX.resource.path, '/other/path.po'])
    )
    assert detailsX[0]['translated_strings'] == 0
    assert detailsX[1]['translated_strings'] == 0

    detailsY = locale_b.parts_stats(project)
    assert len(detailsY) == 2
    assert detailsY[0]['title'] == '/other/path.po'
    assert detailsY[0]['translated_strings'] == 0


@pytest.mark.django_db
def test_locale_parts_stats_pages_not_tied_to_resources(locale_parts):
    """
    Return subpage name and stats.
    """
    locale_a, locale_b, entity_a = locale_parts
    project = entity_a.resource.project
    Subpage.objects.create(project=project, name='Subpage')
    details = locale_a.parts_stats(project)
    assert details[0]['title'] == 'Subpage'
    assert details[0]['translated_strings'] == 0


@pytest.mark.django_db
def test_locale_parts_stats_pages_tied_to_resources(locale_parts):
    """
    Return subpage name and stats for locales resources are available for.
    """
    locale_a, locale_b, entity_a = locale_parts
    project = entity_a.resource.project
    resourceX = Resource.objects.create(
        project=project,
        path='/other/path.po',
    )
    Entity.objects.create(resource=resourceX, string="Entity X")
    TranslatedResource.objects.create(
        resource=resourceX, locale=locale_a,
    )
    TranslatedResource.objects.create(
        resource=resourceX, locale=locale_b,
    )
    sub1 = Subpage.objects.create(
        project=project, name='Subpage',
    )
    sub1.resources.add(resourceX)
    sub2 = Subpage.objects.create(
        project=project, name='Other Subpage',
    )
    sub2.resources.add(resourceX)
    details0 = locale_a.parts_stats(project)
    detailsX = locale_b.parts_stats(project)
    assert details0[0]['title'] == 'Other Subpage'
    assert details0[0]['translated_strings'] == 0
    assert details0[1]['title'] == 'Subpage'
    assert details0[1]['translated_strings'] == 0
    assert detailsX[0]['title'] == 'Other Subpage'
    assert detailsX[0]['translated_strings'] == 0
