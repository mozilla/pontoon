import pytest

from pontoon.base.forms import (
    LocalePermsForm,
    ProjectLocalePermsForm,
    ProjectLocalePermsFormsSet,
)
from pontoon.base.models import PermissionChangelog, ProjectLocale


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
    form = ProjectLocalePermsForm(
        {"translators": []},
        instance=locale_a,
        user=user_a,
    )
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
        changelog_entry0,
        PermissionChangelog.ActionType.ADDED,
        user_a,
        user_c,
        locale_a.translators_group,
    )

    assert_permissionchangelog(
        changelog_entry1,
        PermissionChangelog.ActionType.ADDED,
        user_a,
        user_b,
        locale_a.managers_group,
    )

    # Remove items from groups
    form = LocalePermsForm(
        {"translators": [], "managers": []},
        instance=locale_a,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    changelog_entry3, changelog_entry2 = PermissionChangelog.objects.order_by("-pk")[:2]

    assert_permissionchangelog(
        changelog_entry2,
        PermissionChangelog.ActionType.REMOVED,
        user_a,
        user_c,
        locale_a.translators_group,
    )

    assert_permissionchangelog(
        changelog_entry3,
        PermissionChangelog.ActionType.REMOVED,
        user_a,
        user_b,
        locale_a.managers_group,
    )


@pytest.mark.django_db
def test_project_locale_perms_form_log(
    locale_a, user_a, user_b, user_c, assert_permissionchangelog
):
    # Add new users to groups
    form = ProjectLocalePermsForm(
        {"translators": [user_c.pk]},
        instance=locale_a,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    (changelog_entry0,) = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        PermissionChangelog.ActionType.ADDED,
        user_a,
        user_c,
        locale_a.translators_group,
    )

    # Remove items from groups
    form = ProjectLocalePermsForm(
        {"translators": [], "managers": []},
        instance=locale_a,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    (changelog_entry1,) = PermissionChangelog.objects.order_by("-pk")[:1]

    assert_permissionchangelog(
        changelog_entry1,
        PermissionChangelog.ActionType.REMOVED,
        user_a,
        user_c,
        locale_a.translators_group,
    )


def project_locale_formset_data(project_locale, translators):
    return {
        "project-locale-TOTAL_FORMS": "1",
        "project-locale-INITIAL_FORMS": "1",
        "project-locale-MIN_NUM_FORMS": "0",
        "project-locale-MAX_NUM_FORMS": "1000",
        "project-locale-0-id": str(project_locale.pk),
        "project-locale-0-translators": [str(user.pk) for user in translators],
    }


def project_locale_formset(data, project_locale, user):
    return ProjectLocalePermsFormsSet(
        data,
        prefix="project-locale",
        queryset=ProjectLocale.objects.filter(pk=project_locale.pk),
        form_kwargs={"user": user},
    )


@pytest.mark.django_db
def test_project_locale_formset_log_removal_of_custom_translators(
    project_locale_a, user_a, user_b, user_c, assert_permissionchangelog
):
    """
    Unchecking the custom translators checkbox removes all translators of the
    project, which must be logged like any other permission change.
    """
    project_locale_a.has_custom_translators = True
    project_locale_a.save()
    project_locale_a.translators_group.user_set.add(user_b, user_c)

    data = project_locale_formset_data(project_locale_a, [user_b, user_c])
    formset = project_locale_formset(data, project_locale_a, user_a)

    assert formset.is_valid()
    formset.save()

    project_locale_a.refresh_from_db()
    assert not project_locale_a.has_custom_translators
    assert not project_locale_a.translators_group.user_set.exists()

    entries = PermissionChangelog.objects.order_by("performed_on__email")
    expected_users = sorted([user_b, user_c], key=lambda u: u.email)

    assert entries.count() == len(expected_users)
    for entry, user in zip(entries, expected_users):
        assert_permissionchangelog(
            entry,
            PermissionChangelog.ActionType.REMOVED,
            user_a,
            user,
            project_locale_a.translators_group,
        )


@pytest.mark.django_db
def test_project_locale_formset_log_no_custom_translators(
    project_locale_a, user_a, assert_permissionchangelog
):
    """
    Projects without custom translators have no translators to remove, so
    nothing gets logged.
    """
    data = project_locale_formset_data(project_locale_a, [])
    formset = project_locale_formset(data, project_locale_a, user_a)

    assert formset.is_valid()
    formset.save()

    assert not PermissionChangelog.objects.exists()
