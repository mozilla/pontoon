"""
Tests related to the utils provided in pontoon.teams.libraries
"""
import pytest

from pontoon.base.models import PermissionChangelog
from pontoon.teams.utils import (
    log_user_groups,
    log_group_members,
)
from pontoon.test.factories import (
    GroupFactory,
    UserFactory,
)


@pytest.fixture
def translators_group():
    return GroupFactory.create(name="some translators",)


@pytest.mark.django_db
def test_log_group_members_empty(translators_group, user_a):
    log_group_members(translators_group, user_a, ([], []))

    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_log_group_members_added(translators_group, user_a, assert_permissionchangelog):
    member0, member1, member2 = UserFactory.create_batch(size=3)
    added_members = [member0, member2]

    log_group_members(user_a, translators_group, (added_members, []))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        PermissionChangelog.ActionType.ADDED,
        user_a,
        member0,
        translators_group,
    )
    assert_permissionchangelog(
        changelog_entry1,
        PermissionChangelog.ActionType.ADDED,
        user_a,
        member2,
        translators_group,
    )


@pytest.mark.django_db
def test_log_group_members_removed(
    translators_group, user_a, assert_permissionchangelog
):
    member0, member1, member2 = UserFactory.create_batch(size=3)
    removed_members = [member0, member2]

    log_group_members(user_a, translators_group, ([], removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        PermissionChangelog.ActionType.REMOVED,
        user_a,
        member0,
        translators_group,
    )
    assert_permissionchangelog(
        changelog_entry1,
        PermissionChangelog.ActionType.REMOVED,
        user_a,
        member2,
        translators_group,
    )


@pytest.mark.django_db
def test_log_group_members_mixed(translators_group, user_a, assert_permissionchangelog):
    member0, member1, member2 = UserFactory.create_batch(size=3)
    added_members = [member2]
    removed_members = [member0]

    log_group_members(user_a, translators_group, (added_members, removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        PermissionChangelog.ActionType.ADDED,
        user_a,
        member2,
        translators_group,
    )

    assert_permissionchangelog(
        changelog_entry1,
        PermissionChangelog.ActionType.REMOVED,
        user_a,
        member0,
        translators_group,
    )


@pytest.mark.django_db
def test_log_user_groups_empty(user_a, user_b):
    log_user_groups(user_a, user_b, ([], []))

    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_log_user_groups_added(
    user_a, user_b, assert_permissionchangelog,
):
    group0, group1, group2 = GroupFactory.create_batch(size=3)
    added_groups = [group0, group2]

    log_user_groups(user_a, user_b, (added_groups, []))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0, PermissionChangelog.ActionType.ADDED, user_a, user_b, group0
    )
    assert_permissionchangelog(
        changelog_entry1, PermissionChangelog.ActionType.ADDED, user_a, user_b, group2
    )


@pytest.mark.django_db
def test_log_user_groups_removed(
    user_a, user_b, assert_permissionchangelog,
):
    group0, group1, group2 = GroupFactory.create_batch(size=3)
    removed_members = [group0, group2]

    log_user_groups(user_a, user_b, ([], removed_members))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0, PermissionChangelog.ActionType.REMOVED, user_a, user_b, group0
    )

    assert_permissionchangelog(
        changelog_entry1, PermissionChangelog.ActionType.REMOVED, user_a, user_b, group2
    )


@pytest.mark.django_db
def test_log_user_groups_mixed(
    user_a, user_b, assert_permissionchangelog,
):
    group0, group1, group2 = GroupFactory.create_batch(size=3)
    added_groups = [group2]
    removed_groups = [group0]

    log_user_groups(user_a, user_b, (added_groups, removed_groups))

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()
    assert_permissionchangelog(
        changelog_entry0, PermissionChangelog.ActionType.ADDED, user_a, user_b, group2
    )

    assert_permissionchangelog(
        changelog_entry1, PermissionChangelog.ActionType.REMOVED, user_a, user_b, group0
    )
