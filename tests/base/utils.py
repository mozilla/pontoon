import pytest

from django.contrib.auth import get_user_model

from pontoon.base.models import Resource

from pontoon.base.utils import (
    glob_to_regex,
    get_m2m_changes,
)


def test_util_glob_to_regex():
    assert glob_to_regex('*') == '^.*$'
    assert glob_to_regex('/foo*') == '^\\/foo.*$'
    assert glob_to_regex('*foo') == '^.*foo$'
    assert glob_to_regex('*foo*') == '^.*foo.*$'


@pytest.mark.django_db
def test_util_glob_to_regex_db(resource0, resource1):
    assert resource0 in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert resource1 in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('*')))
        == list(Resource.objects.all()))
    assert (
        resource0
        in Resource.objects.filter(
            path__regex=glob_to_regex('*0*')))
    assert (
        resource1
        not in Resource.objects.filter(
            path__regex=glob_to_regex('*0*')))
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('*0*')))
        == list(Resource.objects.filter(path__contains='0')))


@pytest.mark.django_db
def test_get_m2m_changes_no_change(user0):
    assert get_m2m_changes(
        get_user_model().objects.none(),
        get_user_model().objects.none()
    ) == ([], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user0.pk),
        get_user_model().objects.filter(pk=user0.pk),
    ) == ([], [])


@pytest.mark.django_db
def test_get_m2m_added(user0, user1):
    assert get_m2m_changes(
        get_user_model().objects.none(),
        get_user_model().objects.filter(pk=user1.pk)
    ) == ([user1], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user0.pk),
        get_user_model().objects.filter(pk__in=[user0.pk, user1.pk])
    ) == ([user1], [])


@pytest.mark.django_db
def test_get_m2m_removed(user0, user1):
    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user1.pk),
        get_user_model().objects.none(),
    ) == ([], [user1])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user0.pk, user1.pk]),
        get_user_model().objects.filter(pk=user0.pk),
    ) == ([], [user1])


@pytest.mark.django_db
def test_get_m2m_mixed(user0, user1, userX):
    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user1.pk, userX.pk]),
        get_user_model().objects.filter(pk__in=[user0.pk, user1.pk]),
    ) == ([user0], [userX])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user0.pk, user1.pk]),
        get_user_model().objects.filter(pk__in=[userX.pk]),
    ) == ([userX], [user0, user1])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user1.pk]),
        get_user_model().objects.filter(pk__in=[userX.pk, user0.pk]),
    ) == ([user0, userX], [user1])
