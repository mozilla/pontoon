import pytest

from pontoon.base.models import (
    PermissionChangelog
)
from pontoon.base.forms import (
    LocalePermsForm,
    ProjectLocalePermsForm
)


@pytest.mark.django_db
def test_locale_perms_form_log_no_changes(user0, locale0):
    form = LocalePermsForm(
        {
            'translators': [],
            'managers': []
        },
        instance=locale0,
        user=user0
    )
    assert form.is_valid()

    form.save()

    assert not PermissionChangelog.objects.exists()


@pytest.mark.django_db
def test_project_locale_perms_form_log_no_changes(user0, locale0):
    form = ProjectLocalePermsForm(
        {
            'translators': [],
        },
        instance=locale0,
        user=user0
    )
    assert form.is_valid()

    form.save()

    assert not PermissionChangelog.objects.exists()


@pytest.mark.django_db
def test_locale_perms_form_log(locale0, user0, user1, userX, assert_permissionchangelog):
    # Add new users to groups
    form = LocalePermsForm(
        {
            'translators': [userX.pk],
            'managers': [user1.pk]
        },
        instance=locale0,
        user=user0
    )

    assert form.is_valid()
    form.save()

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user0,
        userX,
        locale0.translators_group
    )

    assert_permissionchangelog(
        changelog_entry1,
        'added',
        user0,
        user1,
        locale0.managers_group
    )

    # Remove items from groups
    form = LocalePermsForm(
        {
            'translators': [],
            'managers': []
        },
        instance=locale0,
        user=user0
    )

    assert form.is_valid()
    form.save()

    changelog_entry3, changelog_entry2 = PermissionChangelog.objects.order_by('-pk')[:2]

    assert_permissionchangelog(
        changelog_entry2,
        'removed',
        user0,
        userX,
        locale0.translators_group
    )

    assert_permissionchangelog(
        changelog_entry3,
        'removed',
        user0,
        user1,
        locale0.managers_group
    )


@pytest.mark.django_db
def test_project_locale_perms_form_log(locale0, user0, user1, userX, assert_permissionchangelog):
    # Add new users to groups
    form = ProjectLocalePermsForm(
        {
            'translators': [userX.pk],
        },
        instance=locale0,
        user=user0
    )

    assert form.is_valid()
    form.save()

    changelog_entry0, = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user0,
        userX,
        locale0.translators_group
    )

    # Remove items from groups
    form = ProjectLocalePermsForm(
        {
            'translators': [],
            'managers': []
        },
        instance=locale0,
        user=user0
    )

    assert form.is_valid()
    form.save()

    changelog_entry1, = PermissionChangelog.objects.order_by('-pk')[:1]

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        user0,
        userX,
        locale0.translators_group
    )
