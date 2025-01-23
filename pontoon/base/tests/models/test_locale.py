from unittest.mock import patch

import pytest

from pontoon.base.models import ProjectLocale


@pytest.mark.django_db
def test_locale_latest_activity_with_latest(translation_a):
    """
    If the locale has a latest_translation and no project is given,
    return it.
    """
    locale = translation_a.locale
    assert locale.get_latest_activity() == translation_a.latest_activity


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
    with patch.object(ProjectLocale, "get_latest_activity") as m:
        m.return_value = "latest"
        assert locale_a.get_latest_activity(project=project_a) == "latest"
        assert m.call_args[0] == (locale_a, project_a)


@pytest.mark.django_db
def test_locale_translators_group(locale_a, locale_b, user_a):
    """
    Tests if user has permission to translate locales after assigment.
    """
    assert user_a.has_perm("base.can_translate_locale") is False
    assert user_a.has_perm("base.can_translate_locale", locale_a) is False
    assert user_a.has_perm("base.can_translate_locale", locale_b) is False

    user_a.groups.add(locale_b.translators_group)
    assert user_a.has_perm("base.can_translate_locale") is False
    assert user_a.has_perm("base.can_translate_locale", locale_a) is False
    assert user_a.has_perm("base.can_translate_locale", locale_b) is True

    user_a.groups.add(locale_a.translators_group)
    assert user_a.has_perm("base.can_translate_locale") is False
    assert user_a.has_perm("base.can_translate_locale", locale_a) is True
    assert user_a.has_perm("base.can_translate_locale", locale_b) is True


@pytest.mark.django_db
def test_locale_managers_group(locale_a, locale_b, user_a):
    """
    Tests if user has permission to manage and translate locales after
    assigment.
    """
    assert user_a.has_perm("base.can_translate_locale") is False
    assert user_a.has_perm("base.can_translate_locale", locale_a) is False
    assert user_a.has_perm("base.can_translate_locale", locale_b) is False
    assert user_a.has_perm("base.can_manage_locale") is False
    assert user_a.has_perm("base.can_manage_locale", locale_a) is False
    assert user_a.has_perm("base.can_manage_locale", locale_b) is False

    user_a.groups.add(locale_b.managers_group)
    assert user_a.has_perm("base.can_translate_locale") is False
    assert user_a.has_perm("base.can_translate_locale", locale_a) is False
    assert user_a.has_perm("base.can_translate_locale", locale_b) is True
    assert user_a.has_perm("base.can_manage_locale") is False
    assert user_a.has_perm("base.can_manage_locale", locale_a) is False
    assert user_a.has_perm("base.can_manage_locale", locale_b) is True

    user_a.groups.add(locale_a.managers_group)
    assert user_a.has_perm("base.can_translate_locale") is False
    assert user_a.has_perm("base.can_translate_locale", locale_a) is True
    assert user_a.has_perm("base.can_translate_locale", locale_b) is True
    assert user_a.has_perm("base.can_manage_locale") is False
    assert user_a.has_perm("base.can_manage_locale", locale_a) is True
    assert user_a.has_perm("base.can_manage_locale", locale_b) is True
