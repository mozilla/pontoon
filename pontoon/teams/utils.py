from pontoon.base.models import PermissionChangelog


def log_user_groups(admin, user, (add_groups, remove_groups)):
    """Log all changes of a user's groups.

    :arg User admin: a super user who perform changes on groups.
    :arg User user: an edited users
    :arg QuerySet add_groups: QuerySet with groups to add
    :arg QuerySet remove_groups: QuerySet with groups to remove
    """
    log_entries = [
        PermissionChangelog(
            action_type='added',
            performed_by=admin,
            performed_on=user,
            group=group,
        )
        for group in add_groups
    ]
    log_entries += [
        PermissionChangelog(
            action_type='removed',
            performed_by=admin,
            performed_on=user,
            group=group,
        )
        for group in remove_groups
    ]
    PermissionChangelog.objects.bulk_create(log_entries)


def log_group_members(manager, group, (add_users, remove_users)):
    """Log all changes a group's members.

    :arg django.contrib.auth.models.User manager: a manager who perform changes on groups.
    :arg django.contrib.auth.models.Group group: group of translators/managers
    :arg django.db.models.QuerySet add_groups: QuerySet with users to add
    :arg django.db.models.QuerySet remove_groups: QuerySet with users to remove
    """
    log_entries = [
        PermissionChangelog(
            action_type='added',
            performed_by=manager,
            performed_on=user,
            group=group,
        )
        for user in add_users
    ]

    log_entries += [
        PermissionChangelog(
            action_type='removed',
            performed_by=manager,
            performed_on=user,
            group=group,
        )
        for user in remove_users
    ]
    PermissionChangelog.objects.bulk_create(log_entries)