import factory
import pytest

from django.contrib.auth import get_user_model

from pontoon.base.models import (
    Locale,
    PermissionChangelog
)
from pontoon.base.forms import (
    LocalePermsForm,
    ProjectLocalePermsForm
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
def assert_permissionchangelog():
    """
    Shortcut assert function for freshly created permission changeset objects.
    """
    def _assert(changelog_item, action_type, performed_by, performed_on, group):
        assert changelog_item.action_type == action_type
        assert changelog_item.performed_by == performed_by
        assert changelog_item.performed_on == performed_on
        assert changelog_item.group == group

    return _assert


@pytest.mark.django_db
def test_locale_perms_form_log_no_changes(user_a, locale):
    form = LocalePermsForm(
        {
            'translators': [],
            'managers': []
        },
        instance=locale,
        user=user_a
    )
    assert form.is_valid()

    form.save()

    assert not PermissionChangelog.objects.exists()


@pytest.mark.django_db
def test_project_locale_perms_form_log_no_changes(user_a, locale):
    form = ProjectLocalePermsForm(
        {
            'translators': [],
        },
        instance=locale,
        user=user_a,
    )
    assert form.is_valid()

    form.save()

    assert not PermissionChangelog.objects.exists()


@pytest.mark.django_db
def test_locale_perms_form_log(
    locale, user_a, user_b, user_c, assert_permissionchangelog
):
    # Add new users to groups
    form = LocalePermsForm(
        {
            'translators': [user_c.pk],
            'managers': [user_b.pk],
        },
        instance=locale,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    changelog_entry0, changelog_entry1 = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user_a,
        user_c,
        locale.translators_group,
    )

    assert_permissionchangelog(
        changelog_entry1,
        'added',
        user_a,
        user_b,
        locale.managers_group,
    )

    # Remove items from groups
    form = LocalePermsForm(
        {
            'translators': [],
            'managers': [],
        },
        instance=locale,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    changelog_entry3, changelog_entry2 = (
        PermissionChangelog.objects.order_by('-pk')[:2]
    )

    assert_permissionchangelog(
        changelog_entry2,
        'removed',
        user_a,
        user_c,
        locale.translators_group,
    )

    assert_permissionchangelog(
        changelog_entry3,
        'removed',
        user_a,
        user_b,
        locale.managers_group,
    )


@pytest.mark.django_db
def test_project_locale_perms_form_log(
    locale, user_a, user_b, user_c, assert_permissionchangelog
):
    # Add new users to groups
    form = ProjectLocalePermsForm(
        {
            'translators': [user_c.pk],
        },
        instance=locale,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    changelog_entry0, = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        user_a,
        user_c,
        locale.translators_group,
    )

    # Remove items from groups
    form = ProjectLocalePermsForm(
        {
            'translators': [],
            'managers': [],
        },
        instance=locale,
        user=user_a,
    )

    assert form.is_valid()
    form.save()

    changelog_entry1, = PermissionChangelog.objects.order_by('-pk')[:1]

    assert_permissionchangelog(
        changelog_entry1,
        'removed',
        user_a,
        user_c,
        locale.translators_group,
    )
