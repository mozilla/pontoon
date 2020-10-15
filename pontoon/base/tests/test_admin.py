import pytest

from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory

from pontoon.base.admin import UserAdmin
from pontoon.base.models import PermissionChangelog
from pontoon.test.factories import (
    GroupFactory,
    LocaleFactory,
)


@pytest.fixture
def locale_c():
    translators_group = GroupFactory.create(name="locale translators",)
    managers_group = GroupFactory.create(name="locale managers",)
    return LocaleFactory.create(
        code="nv",
        name="Na'vi",
        translators_group=translators_group,
        managers_group=managers_group,
    )


@pytest.fixture
def user_form_request():
    """
    Mock for a request object which is passed to every django admin form.
    """

    def _get_user_form_request(request_user, user, **override_fields):
        rf = RequestFactory()
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )

        form_request = {f: (getattr(user, f, "") or "") for f in fields}
        form_request["date_joined_0"] = "2018-01-01"
        form_request["date_joined_1"] = "00:00:00"

        form_request.update(override_fields)

        request = rf.post("/dummy/", form_request,)
        request.user = request_user
        return request

    return _get_user_form_request


@pytest.fixture
def get_useradmin_form():
    """
    Get a UserAdmin form instance.
    """

    def _get_user_admin_form(request, user):
        useradmin = UserAdmin(User, AdminSite(),)
        form = useradmin.get_form(request=request, obj=user,)
        return (
            useradmin,
            form(request.POST, instance=user, initial={"password": "password"},),
        )

    return _get_user_admin_form


@pytest.mark.django_db
def test_user_admin_form_log_no_changes(
    user_a, user_b, user_form_request, get_useradmin_form,
):
    _, form = get_useradmin_form(user_form_request(user_a, user_b), user_b,)

    assert form.is_valid()

    form.save()
    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_user_admin_form_log_add_groups(
    locale_c,
    user_a,
    user_b,
    user_form_request,
    get_useradmin_form,
    assert_permissionchangelog,
):
    request = user_form_request(user_a, user_b, groups=[locale_c.managers_group.pk],)
    useradmin, form = get_useradmin_form(request, user_b,)
    assert form.is_valid()

    useradmin.save_model(request, user_b, form, True)

    (changelog_entry0,) = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0, "added", user_a, user_b, locale_c.managers_group,
    )


@pytest.mark.django_db
def test_user_admin_form_log_removed_groups(
    locale_c,
    user_a,
    user_b,
    user_form_request,
    get_useradmin_form,
    assert_permissionchangelog,
):
    user_b.groups.add(locale_c.managers_group)
    request = user_form_request(user_a, user_b, groups=[],)
    useradmin, form = get_useradmin_form(request, user_b,)
    assert form.is_valid()

    useradmin.save_model(request, user_b, form, True)

    (changelog_entry0,) = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0, "removed", user_a, user_b, locale_c.managers_group,
    )
