from pontoon.base.models import PermissionChangelog


def log_user_groups(admin, user, changed_groups):
    """Log all changes of a user's groups.

    :arg User admin: a super user who perform changes on groups.
    :arg User user: an edited users
    :arg tuple changed_groups: Contains two querysets:
        * add - QuerySet with groups to add
        * remove - QuerySet with groups to remove
    """
    add_groups, remove_groups = changed_groups
    log_entries = [
        PermissionChangelog(
            action_type=PermissionChangelog.ActionType.ADDED,
            performed_by=admin,
            performed_on=user,
            group=group,
        )
        for group in add_groups
    ]
    log_entries += [
        PermissionChangelog(
            action_type=PermissionChangelog.ActionType.REMOVED,
            performed_by=admin,
            performed_on=user,
            group=group,
        )
        for group in remove_groups
    ]
    PermissionChangelog.objects.bulk_create(log_entries)


def log_group_members(manager, group, changed_groups):
    """Log all changes a group's members.

    :arg django.contrib.auth.models.User manager: a manager who perform changes on groups.
    :arg django.contrib.auth.models.Group group: group of translators/managers
    :arg tuple changed_groups: Contains two querysets:
        * add - QuerySet with groups to add
        * remove - QuerySet with groups to remove
    """
    add_users, remove_users = changed_groups
    log_entries = [
        PermissionChangelog(
            action_type=PermissionChangelog.ActionType.ADDED,
            performed_by=manager,
            performed_on=user,
            group=group,
        )
        for user in add_users
    ]

    log_entries += [
        PermissionChangelog(
            action_type=PermissionChangelog.ActionType.REMOVED,
            performed_by=manager,
            performed_on=user,
            group=group,
        )
        for user in remove_users
    ]
    PermissionChangelog.objects.bulk_create(log_entries)
