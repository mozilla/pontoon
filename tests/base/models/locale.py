
import pytest

from mock import patch

from pontoon.base.models import (
    Entity, ProjectLocale, Resource, Subpage, TranslatedResource)


@pytest.mark.django_db
def test_locale_latest_activity_with_latest(translation0):
    """
    If the locale has a latest_translation and no project is given,
    return it.
    """
    locale = translation0.locale
    assert (
        locale.get_latest_activity()
        == translation0.latest_activity)


@pytest.mark.django_db
def test_locale_latest_activity_without_latest(localeX):
    """
    If the locale doesn't have a latest_translation and no project
    is given, return None.
    """
    assert localeX.get_latest_activity() is None


@pytest.mark.django_db
def test_locale_latest_activity_with_project(locale0, project0):
    """
    If a locale is given, defer to
    ProjectLocale.get_latest_activity.
    """
    ProjectLocale.objects.create(
        project=project0, locale=locale0)

    with patch.object(ProjectLocale, 'get_latest_activity') as m:
        m.return_value = 'latest'
        assert locale0.get_latest_activity(project=project0) == 'latest'
        assert m.call_args[0] == (locale0, project0)


@pytest.mark.django_db
def test_locale_translators_group(locale0, locale1, user0):
    """
    Tests if user has permission to translate locales after assigment.
    """
    assert user0.has_perm('base.can_translate_locale') is False
    assert user0.has_perm('base.can_translate_locale', locale0) is False
    assert user0.has_perm('base.can_translate_locale', locale1) is False

    user0.groups.add(locale1.translators_group)
    assert user0.has_perm('base.can_translate_locale') is False
    assert user0.has_perm('base.can_translate_locale', locale0) is False
    assert user0.has_perm('base.can_translate_locale', locale1) is True

    user0.groups.add(locale0.translators_group)
    assert user0.has_perm('base.can_translate_locale') is False
    assert user0.has_perm('base.can_translate_locale', locale0) is True
    assert user0.has_perm('base.can_translate_locale', locale1) is True


@pytest.mark.django_db
def test_locale_managers_group(locale0, locale1, user0):
    """
    Tests if user has permission to manage and translate locales after
    assigment.
    """
    assert user0.has_perm('base.can_translate_locale') is False
    assert user0.has_perm('base.can_translate_locale', locale0) is False
    assert user0.has_perm('base.can_translate_locale', locale1) is False
    assert user0.has_perm('base.can_manage_locale') is False
    assert user0.has_perm('base.can_manage_locale', locale0) is False
    assert user0.has_perm('base.can_manage_locale', locale1) is False

    user0.groups.add(locale1.managers_group)
    assert user0.has_perm('base.can_translate_locale') is False
    assert user0.has_perm('base.can_translate_locale', locale0) is False
    assert user0.has_perm('base.can_translate_locale', locale1) is True
    assert user0.has_perm('base.can_manage_locale') is False
    assert user0.has_perm('base.can_manage_locale', locale0) is False
    assert user0.has_perm('base.can_manage_locale', locale1) is True

    user0.groups.add(locale0.managers_group)
    assert user0.has_perm('base.can_translate_locale') is False
    assert user0.has_perm('base.can_translate_locale', locale0) is True
    assert user0.has_perm('base.can_translate_locale', locale1) is True
    assert user0.has_perm('base.can_manage_locale') is False
    assert user0.has_perm('base.can_manage_locale', locale0) is True
    assert user0.has_perm('base.can_manage_locale', locale1) is True


@pytest.mark.django_db
def test_locale_parts_stats_no_page_one_resource(locale_parts):
    """
    Return resource paths and stats if no subpage and one resource defined.
    """
    locale0, locale1, entity0 = locale_parts
    project = entity0.resource.project
    details = locale0.parts_stats(project)
    assert len(details) == 2
    assert details[0]['title'] == entity0.resource.path
    assert details[0]['translated_strings'] == 0


@pytest.mark.django_db
def test_locale_parts_stats_no_page_multiple_resources(locale_parts):
    """
    Return resource paths and stats for locales resources are available for.
    """
    locale0, locale1, entity0 = locale_parts
    project = entity0.resource.project
    resourceX = Resource.objects.create(
        total_strings=1,
        project=project,
        path='/other/path.po')
    Entity.objects.create(resource=resourceX, string="Entity X")
    TranslatedResource.objects.create(
        resource=resourceX, locale=locale0)
    TranslatedResource.objects.create(
        resource=resourceX, locale=locale1)

    # results are sorted by title

    details0 = locale0.parts_stats(project)
    assert (
        [detail["title"] for detail in details0][:2]
        == sorted([entity0.resource.path, '/other/path.po']))
    assert details0[0]['translated_strings'] == 0
    assert details0[1]['translated_strings'] == 0

    detailsX = locale1.parts_stats(project)
    assert len(detailsX) == 2
    assert detailsX[0]['title'] == '/other/path.po'
    assert detailsX[0]['translated_strings'] == 0


@pytest.mark.django_db
def test_locale_parts_stats_pages_not_tied_to_resources(locale_parts):
    """
    Return subpage name and stats.
    """
    locale0, locale1, entity0 = locale_parts
    project = entity0.resource.project
    Subpage.objects.create(project=project, name='Subpage')
    details = locale0.parts_stats(project)
    assert details[0]['title'] == 'Subpage'
    assert details[0]['translated_strings'] == 0


@pytest.mark.django_db
def test_locale_parts_stats_pages_tied_to_resources(locale_parts):
    """
    Return subpage name and stats for locales resources are available for.
    """
    locale0, locale1, entity0 = locale_parts
    project = entity0.resource.project
    resourceX = Resource.objects.create(
            project=project,
            path='/other/path.po')
    Entity.objects.create(resource=resourceX, string="Entity X")
    TranslatedResource.objects.create(
        resource=resourceX, locale=locale0)
    TranslatedResource.objects.create(
        resource=resourceX, locale=locale1)
    sub1 = Subpage.objects.create(
        project=project, name='Subpage')
    sub1.resources.add(resourceX)
    sub2 = Subpage.objects.create(
        project=project, name='Other Subpage')
    sub2.resources.add(resourceX)
    details0 = locale0.parts_stats(project)
    detailsX = locale1.parts_stats(project)
    assert details0[0]['title'] == 'Other Subpage'
    assert details0[0]['translated_strings'] == 0
    assert details0[1]['title'] == 'Subpage'
    assert details0[1]['translated_strings'] == 0
    assert detailsX[0]['title'] == 'Other Subpage'
    assert detailsX[0]['translated_strings'] == 0
