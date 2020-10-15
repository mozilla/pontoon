import pytest

from pontoon.base.forms import LocalePermsForm, ProjectLocalePermsForm
from pontoon.base.models import PermissionChangelog


@pytest.mark.django_db
def test_locale_perms_form_log_no_changes(user_a, locale_a):
    form = LocalePermsForm(
        {"translators": [], "managers": []}, instance=locale_a, user=user_a
    )
    assert form.is_valid()

    form.save()

    assert not PermissionChangelog.objects.exists()


@pytest.mark.django_db
def test_project_locale_perms_form_log_no_changes(user_a, locale_a):
    form = ProjectLocalePermsForm({"translators": []}, instance=locale_a, user=user_a,)
    assert form.is_valid()

    form.save()

    assert not PermissionChangelog.objects.exists()


@pytest.mark.django_db
def test_locale_perms_form_log(
    locale_a, user_a, user_b, user_c, assert_permissionchangelog
):
    # Add new users to groups
    form = LocalePermsForm(
        {"translators": [user_c.pk], "managers": [user_b.pk]},
        instance=locale_a,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0, "added", user_a, user_c, locale_a.translators_group,
    )

    assert_permissionchangelog(
        changelog_entry1, "added", user_a, user_b, locale_a.managers_group,
    )

    # Remove items from groups
    form = LocalePermsForm(
        {"translators": [], "managers": []}, instance=locale_a, user=user_a,
    )

    assert form.is_valid()
    form.save()

    changelog_entry3, changelog_entry2 = PermissionChangelog.objects.order_by("-pk")[:2]

    assert_permissionchangelog(
        changelog_entry2, "removed", user_a, user_c, locale_a.translators_group,
    )

    assert_permissionchangelog(
        changelog_entry3, "removed", user_a, user_b, locale_a.managers_group,
    )


@pytest.mark.django_db
def test_project_locale_perms_form_log(
    locale_a, user_a, user_b, user_c, assert_permissionchangelog
):
    # Add new users to groups
    form = ProjectLocalePermsForm(
        {"translators": [user_c.pk]}, instance=locale_a, user=user_a,
    )

    assert form.is_valid()
    form.save()

    (changelog_entry0,) = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0, "added", user_a, user_c, locale_a.translators_group,
    )

    # Remove items from groups
    form = ProjectLocalePermsForm(
        {"translators": [], "managers": []}, instance=locale_a, user=user_a,
    )

    assert form.is_valid()
    form.save()

    (changelog_entry1,) = PermissionChangelog.objects.order_by("-pk")[:1]

    assert_permissionchangelog(
        changelog_entry1, "removed", user_a, user_c, locale_a.translators_group,
    )
