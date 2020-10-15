import pytest

from pontoon.base.models import ProjectLocale
from pontoon.test.factories import ProjectLocaleFactory


@pytest.mark.django_db
def test_projectlocale_latest_activity_doesnt_exist(project_a, locale_a):
    """
    If no ProjectLocale exists with the given project/locale,
    return None.
    """
    assert not (
        ProjectLocale.objects.filter(project=project_a, locale=locale_a).exists()
    )
    assert ProjectLocale.get_latest_activity(project_a, locale_a) is None


@pytest.mark.django_db
def test_projectlocale_latest_activity_no_latest(project_a, locale_a):
    """
    If the matching ProjectLocale has no latest_translation, return
    None.
    """
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
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
    project_locale = ProjectLocaleFactory.create(
        project=project_a, locale=locale_a, has_custom_translators=True,
    )

    assert user_a.can_translate(locale=locale_a, project=project_a) is False

    user_a.groups.add(project_locale.translators_group)
    assert user_a.can_translate(locale=locale_a, project=project_a) is True

    project_locale.has_custom_translators = False
    project_locale.save()
    assert user_a.can_translate(locale=locale_a, project=project_a) is False
