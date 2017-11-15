
import pytest

from pontoon.base.models import ProjectLocale


@pytest.mark.django_db
def test_projectlocale_latest_activity_doesnt_exist(projectX, localeX):
    """
    If no ProjectLocale exists with the given project/locale,
    return None.
    """
    assert not (
        ProjectLocale.objects
                     .filter(project=projectX, locale=localeX)
                     .exists())
    assert (
        ProjectLocale.get_latest_activity(projectX, localeX)
        is None)


@pytest.mark.django_db
def test_projectlocale_latest_activity_no_latest(projectX, localeX):
    """
    If the matching ProjectLocale has no latest_translation, return
    None.
    """
    ProjectLocale.objects.create(
        project=projectX, locale=localeX)
    assert (
        ProjectLocale.get_latest_activity(projectX, localeX)
        is None)


@pytest.mark.django_db
def test_projectlocale_latest_activity_success(translation0):
    """
    If the matching ProjectLocale has a latest_translation, return
    it's latest_activity.
    """
    project = translation0.entity.resource.project
    locale = translation0.locale
    assert ProjectLocale.get_latest_activity(project, locale)
    assert (
        ProjectLocale.get_latest_activity(project, locale)
        == translation0.latest_activity)


@pytest.mark.django_db
def test_projectlocale_translators_group(projectX, localeX, user0):
    """
    Tests if user has permission to translate project at specific
    locale after assigment.
    """
    project_locale = ProjectLocale.objects.create(
        project=projectX,
        locale=localeX,
        has_custom_translators=True)

    assert user0.can_translate(locale=localeX, project=projectX) is False

    user0.groups.add(project_locale.translators_group)
    assert user0.can_translate(locale=localeX, project=projectX) is True

    project_locale.has_custom_translators = False
    project_locale.save()
    assert user0.can_translate(locale=localeX, project=projectX) is False
