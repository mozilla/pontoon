"""
Tests related to the utils provided in pontoon.teams.libraries
"""
import pytest

from pontoon.base.models import (
    PermissionChangelog,
)
from pontoon.teams.utils import (
    log_user_groups,
    log_group_members,
)


@pytest.mark.django_db
def test_log_group_members_empty(translators_group0, user0):
    log_group_members(translators_group0, user0, ([], []))

    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_log_group_members_added(
        translators_group0,
        user0,
        user_factory,
        assert_permissionchangelog):
    member0, member1, member2 = user_factory(batch=3)
    added_members = [member0, member2]

    log_group_members(user0, translators_group0, (added_members, []))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user0,
        member0,
        translators_group0
    )
    assert_permissionchangelog(
        changelog_entry1,
        'added',
        user0,
        member2,
        translators_group0
    )


@pytest.mark.django_db
def test_log_group_members_removed(
        translators_group0,
        user0,
        user_factory,
        assert_permissionchangelog):
    member0, member1, member2 = user_factory(batch=3)
    removed_members = [member0, member2]

    log_group_members(user0, translators_group0, ([], removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'removed',
        user0,
        member0,
        translators_group0
    )
    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        user0,
        member2,
        translators_group0
    )


@pytest.mark.django_db
def test_log_group_members_mixed(
        translators_group0,
        user0,
        user_factory,
        assert_permissionchangelog):
    member0, member1, member2 = user_factory(batch=3)
    added_members = [member2]
    removed_members = [member0]

    log_group_members(user0, translators_group0, (added_members, removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user0,
        member2,
        translators_group0
    )

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        user0,
        member0,
        translators_group0
    )


@pytest.mark.django_db
def test_log_user_groups_empty(user0, user1):
    log_user_groups(user0, user1, ([], []))

    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_log_user_groups_added(user0, user1, group_factory, assert_permissionchangelog):
    group0, group1, group2 = group_factory(batch=3)
    added_groups = [group0, group2]

    log_user_groups(user0, user1, (added_groups, []))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user0,
        user1,
        group0
    )
    assert_permissionchangelog(
        changelog_entry1,
        'added',
        user0,
        user1,
        group2
    )


@pytest.mark.django_db
def test_log_user_groups_removed(user0, user1, group_factory, assert_permissionchangelog):
    group0, group1, group2 = group_factory(batch=3)
    removed_members = [group0, group2]

    log_user_groups(user0, user1, ([], removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'removed',
        user0,
        user1,
        group0
    )

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        user0,
        user1,
        group2
    )


@pytest.mark.django_db
def test_log_user_groups_mixed(user0, user1, group_factory, assert_permissionchangelog):
    group0, group1, group2 = group_factory(batch=3)
    added_groups = [group2]
    removed_groups = [group0]

    log_user_groups(user0, user1, (added_groups, removed_groups))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()
    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user0,
        user1,
        group2
    )

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        user0,
        user1,
        group0
    )
