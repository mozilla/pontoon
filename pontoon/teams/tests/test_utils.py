"""
Tests related to the utils provided in pontoon.teams.libraries
"""
import factory
import pytest

from django.contrib.auth import get_user_model

from pontoon.base.models import (
    PermissionChangelog,
)
from pontoon.teams.utils import (
    log_user_groups,
    log_group_members,
)
from pontoon.base.models import (
    Group,
)


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group


def group_factory(batch=1):
    return [
        GroupFactory(
            name='group of users %s' % i,
        )
        for i in range(batch)
    ]


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()


def user_factory(batch=1):
    return [
        UserFactory(
            username='fake user %s' % i,
            email='user%s@example.org' % i,
        )
        for i in range(batch)
    ]


@pytest.fixture
def fake_user():
    return UserFactory(
        username="fake_user",
        email="fake_user@example.org"
    )


@pytest.fixture
def other_user():
    return UserFactory(
        username="other_user",
        email="other_user@example.org"
    )


@pytest.fixture
def assert_permissionchangelog():
    """
    Shortcut assert function for freshly created permission changeset objects.
    """
    def test(changelog_item, action_type, performed_by, performed_on, group):
        assert changelog_item.action_type == action_type
        assert changelog_item.performed_by == performed_by
        assert changelog_item.performed_on == performed_on
        assert changelog_item.group == group

    return test


@pytest.fixture
def translators_group():
    return Group.objects.create(
        name='some translators',
    )


@pytest.mark.django_db
def test_log_group_members_empty(translators_group, fake_user):
    log_group_members(translators_group, fake_user, ([], []))

    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_log_group_members_added(
    translators_group,
    fake_user,
    assert_permissionchangelog
):
    member0, member1, member2 = user_factory(batch=3)
    added_members = [member0, member2]

    log_group_members(fake_user, translators_group, (added_members, []))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        fake_user,
        member0,
        translators_group
    )
    assert_permissionchangelog(
        changelog_entry1,
        'added',
        fake_user,
        member2,
        translators_group
    )


@pytest.mark.django_db
def test_log_group_members_removed(
    translators_group,
    fake_user,
    assert_permissionchangelog
):
    member0, member1, member2 = user_factory(batch=3)
    removed_members = [member0, member2]

    log_group_members(fake_user, translators_group, ([], removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'removed',
        fake_user,
        member0,
        translators_group
    )
    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        fake_user,
        member2,
        translators_group
    )


@pytest.mark.django_db
def test_log_group_members_mixed(
    translators_group,
    fake_user,
    assert_permissionchangelog
):
    member0, member1, member2 = user_factory(batch=3)
    added_members = [member2]
    removed_members = [member0]

    log_group_members(
        fake_user,
        translators_group,
        (added_members, removed_members)
    )

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        fake_user,
        member2,
        translators_group
    )

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        fake_user,
        member0,
        translators_group
    )


@pytest.mark.django_db
def test_log_user_groups_empty(fake_user, other_user):
    log_user_groups(fake_user, other_user, ([], []))

    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_log_user_groups_added(
    fake_user,
    other_user,
    assert_permissionchangelog,
):
    group0, group1, group2 = group_factory(batch=3)
    added_groups = [group0, group2]

    log_user_groups(fake_user, other_user, (added_groups, []))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        fake_user,
        other_user,
        group0
    )
    assert_permissionchangelog(
        changelog_entry1,
        'added',
        fake_user,
        other_user,
        group2
    )


@pytest.mark.django_db
def test_log_user_groups_removed(
    fake_user,
    other_user,
    assert_permissionchangelog,
):
    group0, group1, group2 = group_factory(batch=3)
    removed_members = [group0, group2]

    log_user_groups(fake_user, other_user, ([], removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'removed',
        fake_user,
        other_user,
        group0
    )

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        fake_user,
        other_user,
        group2
    )


@pytest.mark.django_db
def test_log_user_groups_mixed(
    fake_user,
    other_user,
    assert_permissionchangelog,
):
    group0, group1, group2 = group_factory(batch=3)
    added_groups = [group2]
    removed_groups = [group0]

    log_user_groups(fake_user, other_user, (added_groups, removed_groups))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()
    assert_permissionchangelog(
        changelog_entry0,
        'added',
        fake_user,
        other_user,
        group2
    )

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        fake_user,
        other_user,
        group0
    )
