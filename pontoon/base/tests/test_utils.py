from __future__ import absolute_import
import sys

import pytest

from django.contrib.auth import get_user_model

from pontoon.base.models import (
    Project,
    Resource,
)
from pontoon.base.utils import (
    aware_datetime,
    extension_in,
    get_m2m_changes,
    get_object_or_none,
    glob_to_regex,
    latest_datetime,
)


def test_util_glob_to_regex():
    assert glob_to_regex('*') == '^([^/]*)$'
    assert glob_to_regex('*foo') == '^([^/]*)foo$'
    assert glob_to_regex('*foo*') == '^([^/]*)foo([^/]*)$'


@pytest.mark.skipif(
    sys.version_info[0] > 2,
    reason="re.escape escapes non-alphanum characters differently between Python 2 and Python 3."
)
def test_util_glob_to_regex_python2():
    assert glob_to_regex('{ variable }/foo*') == r'^\/foo([^/]*)$'
    assert glob_to_regex('bar/**/foo*') == r'^bar\/(.*)foo([^/]*)$'


def test_util_glob_to_regex_unsupported_variables():
    """Raise an error if the user tries to use variables in the glob expression."""
    with pytest.raises(ValueError):
        glob_to_regex('{ variable }/smth')

@pytest.mark.skipif(
    sys.version_info[0] < 3,
    reason="re.escape escapes non-alphanum characters differently between Python 2 and Python 3."
)
def test_util_glob_to_regex_python3():
    assert glob_to_regex('{ variable }/foo*') == '^/foo([^/]*)$'
    assert glob_to_regex('bar/**/foo*') == '^bar/(.*)foo([^/]*)$'


@pytest.mark.django_db
def test_util_glob_to_regex_db(resource_a, resource_b):
    assert resource_a in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert resource_b in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('*')))
        == list(Resource.objects.all())
    )

    assert resource_a in Resource.objects.filter(path__regex=glob_to_regex('**'))
    assert resource_b in Resource.objects.filter(path__regex=glob_to_regex('**'))
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('**')))
        == list(Resource.objects.all())
    )

    assert (
        resource_a
        in Resource.objects.filter(
            path__regex=glob_to_regex('*a*')
        )
    )
    assert (
        resource_b
        not in Resource.objects.filter(
            path__regex=glob_to_regex('*a*')
        )
    )
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('*a*')))
        == list(Resource.objects.filter(path__contains='a'))
    )


@pytest.mark.django_db
def test_get_m2m_changes_no_change(user_a):
    assert get_m2m_changes(
        get_user_model().objects.none(),
        get_user_model().objects.none()
    ) == ([], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_a.pk),
        get_user_model().objects.filter(pk=user_a.pk),
    ) == ([], [])


@pytest.mark.django_db
def test_get_m2m_added(user_a, user_b):
    assert get_m2m_changes(
        get_user_model().objects.none(),
        get_user_model().objects.filter(pk=user_b.pk)
    ) == ([user_b], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_a.pk),
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk])
    ) == ([user_b], [])


@pytest.mark.django_db
def test_get_m2m_removed(user_a, user_b):
    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_b.pk),
        get_user_model().objects.none(),
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
    assert extension_in('filename.txt', ['bat', 'txt'])
    assert extension_in('filename.biff', ['biff'])
    assert extension_in('filename.tar.gz', ['gz'])

    assert not extension_in('filename.txt', ['png', 'jpg'])
    assert not extension_in('.dotfile', ['bat', 'txt'])

    # Unintuitive, but that's how splitext works.
    assert not extension_in('filename.tar.gz', ['tar.gz'])


@pytest.mark.django_db
def test_util_base_get_object_or_none(project_a):
    assert get_object_or_none(Project, slug='does-not-exist') is None
    assert get_object_or_none(Project, slug=project_a.slug) == project_a


def test_util_base_latest_datetime():
    larger = aware_datetime(2015, 1, 1)
    smaller = aware_datetime(2014, 1, 1)
    assert latest_datetime([None, None, None]) is None
    assert latest_datetime([None, larger]) == larger
    assert latest_datetime([None, smaller, larger]) == larger
