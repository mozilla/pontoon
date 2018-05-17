import factory
import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory

from pontoon.base.admin import UserAdmin
from pontoon.base.models import Group, Locale, PermissionChangelog


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()


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
def locale():
    translators_group = Group.objects.create(
        name='locale translators',
    )
    managers_group = Group.objects.create(
        name='locale managers',
    )
    return Locale.objects.create(
        code="kg",
        name="Klingon",
        translators_group=translators_group,
        managers_group=managers_group,
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


@pytest.fixture
def user_form_request():
    """
    Mock for a request object which is passed to every django admin form.
    """
    def _get_user_form_request(request_user, user, **override_fields):
        rf = RequestFactory()
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )

        form_request = {f: (getattr(user, f, '') or '') for f in fields}
        form_request['date_joined_0'] = '2018-01-01'
        form_request['date_joined_1'] = '00:00:00'

        form_request.update(override_fields)

        request = rf.post(
            '/dummy/',
            form_request,
        )
        request.user = request_user
        return request

    return _get_user_form_request


@pytest.fixture
def get_useradmin_form():
    """
    Get a UserAdmin form instance.
    """
    def _get_user_admin_form(request, user):
        useradmin = UserAdmin(
            User,
            AdminSite(),
        )
        form = useradmin.get_form(
            request=request,
            obj=user,
        )
        return useradmin, form(
            request.POST,
            instance=user,
            initial={'password': 'password'},
        )

    return _get_user_admin_form


@pytest.mark.django_db
def test_user_admin_form_log_no_changes(
    fake_user,
    other_user,
    user_form_request,
    get_useradmin_form,
):
    _, form = get_useradmin_form(
        user_form_request(fake_user, other_user),
        other_user,
    )

    assert form.is_valid()

    form.save()
    assert list(PermissionChangelog.objects.all()) == []


@pytest.mark.django_db
def test_user_admin_form_log_add_groups(
    locale,
    fake_user,
    other_user,
    user_form_request,
    get_useradmin_form,
    assert_permissionchangelog,
):
    request = user_form_request(
        fake_user,
        other_user,
        groups=[
            locale.managers_group.pk,
        ],
    )
    useradmin, form = get_useradmin_form(
        request,
        other_user,
    )
    assert form.is_valid()

    useradmin.save_model(request, other_user, form, True)

    changelog_entry0, = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'added',
        fake_user,
        other_user,
        locale.managers_group,
    )


@pytest.mark.django_db
def test_user_admin_form_log_removed_groups(
    locale,
    fake_user,
    other_user,
    user_form_request,
    get_useradmin_form,
    assert_permissionchangelog,
):
    other_user.groups.add(locale.managers_group)
    request = user_form_request(
        fake_user,
        other_user,
        groups=[],
    )
    useradmin, form = get_useradmin_form(
        request,
        other_user,
    )
    assert form.is_valid()

    useradmin.save_model(request, other_user, form, True)

    changelog_entry0, = PermissionChangelog.objects.all()

    assert_permissionchangelog(
        changelog_entry0,
        'removed',
        fake_user,
        other_user,
        locale.managers_group,
    )
