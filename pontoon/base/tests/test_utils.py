import pytest

from django.contrib.auth import get_user_model

from pontoon.base.models import Project
from pontoon.base.utils import (
    aware_datetime,
    extension_in,
    get_m2m_changes,
    get_object_or_none,
    latest_datetime,
)


@pytest.mark.django_db
def test_get_m2m_changes_no_change(user_a):
    assert get_m2m_changes(
        get_user_model().objects.none(), get_user_model().objects.none()
    ) == ([], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_a.pk),
        get_user_model().objects.filter(pk=user_a.pk),
    ) == ([], [])


@pytest.mark.django_db
def test_get_m2m_added(user_a, user_b):
    assert get_m2m_changes(
        get_user_model().objects.none(), get_user_model().objects.filter(pk=user_b.pk)
    ) == ([user_b], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_a.pk),
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
    ) == ([user_b], [])


@pytest.mark.django_db
def test_get_m2m_removed(user_a, user_b):
    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_b.pk), get_user_model().objects.none(),
    ) == ([], [user_b])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
        get_user_model().objects.filter(pk=user_a.pk),
    ) == ([], [user_b])


@pytest.mark.django_db
def test_get_m2m_mixed(user_a, user_b, user_c):
    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_b.pk, user_c.pk]),
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
    ) == ([user_a], [user_c])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
        get_user_model().objects.filter(pk__in=[user_c.pk]),
    ) == ([user_c], [user_a, user_b])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_b.pk]),
        get_user_model().objects.filter(pk__in=[user_c.pk, user_a.pk]),
    ) == ([user_a, user_c], [user_b])


def test_util_base_extension_in():
    assert extension_in("filename.txt", ["bat", "txt"])
    assert extension_in("filename.biff", ["biff"])
    assert extension_in("filename.tar.gz", ["gz"])

    assert not extension_in("filename.txt", ["png", "jpg"])
    assert not extension_in(".dotfile", ["bat", "txt"])

    # Unintuitive, but that's how splitext works.
    assert not extension_in("filename.tar.gz", ["tar.gz"])


@pytest.mark.django_db
def test_util_base_get_object_or_none(project_a):
    assert get_object_or_none(Project, slug="does-not-exist") is None
    assert get_object_or_none(Project, slug=project_a.slug) == project_a


def test_util_base_latest_datetime():
    larger = aware_datetime(2015, 1, 1)
    smaller = aware_datetime(2014, 1, 1)
    assert latest_datetime([None, None, None]) is None
    assert latest_datetime([None, larger]) == larger
    assert latest_datetime([None, smaller, larger]) == larger
