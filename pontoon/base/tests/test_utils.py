import factory
import pytest

from django.contrib.auth import get_user_model

from pontoon.base.models import (
    Locale,
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


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()


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
def user_c():
    return UserFactory(
        username="user_c",
        email="user_c@example.org"
    )


@pytest.fixture
def locale():
    return Locale.objects.create(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def project():
    return Project.objects.create(
        slug="project", name="Project"
    )


@pytest.fixture
def resource_a(locale, project):
    return Resource.objects.create(
        project=project, path="resource_a.po", format="po"
    )


@pytest.fixture
def resource_b(locale, project):
    return Resource.objects.create(
        project=project, path="resource_b.po", format="po"
    )


def test_util_glob_to_regex():
    assert glob_to_regex('*') == '^.*$'
    assert glob_to_regex('/foo*') == '^\\/foo.*$'
    assert glob_to_regex('*foo') == '^.*foo$'
    assert glob_to_regex('*foo*') == '^.*foo.*$'


@pytest.mark.django_db
def test_util_glob_to_regex_db(resource_a, resource_b):
    assert resource_a in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert resource_b in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('*')))
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
def test_util_base_get_object_or_none(project):
    assert get_object_or_none(Project, slug='does-not-exist') is None
    assert get_object_or_none(Project, slug='project') == project


def test_util_base_latest_datetime():
    larger = aware_datetime(2015, 1, 1)
    smaller = aware_datetime(2014, 1, 1)
    assert latest_datetime([None, None, None]) is None
    assert latest_datetime([None, larger]) == larger
    assert latest_datetime([None, smaller, larger]) == larger
