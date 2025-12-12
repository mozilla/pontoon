from collections import OrderedDict
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from django.http import HttpResponse
from django.urls import reverse
from django.utils.timezone import make_aware, now

from pontoon.api.models import PersonalAccessToken
from pontoon.base.models import User
from pontoon.base.tests import (
    LocaleFactory,
    TranslationFactory,
)
from pontoon.base.utils import aware_datetime
from pontoon.contributors import views


def commajoin(*items):
    """
    Small helper function that joins all items by comma and maps types
    of items into strings.
    """
    return ",".join(map(str, items))


@pytest.fixture
def settings_url():
    return reverse("pontoon.contributors.settings")


@pytest.mark.django_db
def test_profileform_invalid_first_name(member):
    params = {
        "first_name": '<aa>"\'"',
    }

    response = member.client.post("/user/attributes/field/", params)
    assert b"Enter a valid value." in response.content


@pytest.mark.django_db
def test_profileform_missing_first_name(member):
    params = {"first_name": ""}

    response = member.client.post("/user/attributes/field/", params)
    assert response.content.count(b"This field is required.") == 1


@pytest.mark.django_db
def test_profileform_valid_first_name(member):
    params = {"first_name": "contributor"}

    response = member.client.post("/user/attributes/field/", params)
    assert b'{"status": true}' in response.content


@pytest.mark.django_db
def test_profileform_user_locales_order(member):
    locale1, locale2, locale3 = LocaleFactory.create_batch(3)

    response = member.client.post(
        "/user/attributes/selector/",
        {
            "locales_order": commajoin(
                locale2.pk,
                locale1.pk,
                locale3.pk,
            ),
        },
    )

    assert response.status_code == 200
    assert list(User.objects.get(pk=member.user.pk).profile.sorted_locales) == [
        locale2,
        locale1,
        locale3,
    ]
    # Test if you can clear all locales
    response = member.client.post(
        "/user/attributes/selector/",
        {"locales_order": ""},
    )
    assert response.status_code == 200
    assert list(User.objects.get(pk=member.user.pk).profile.sorted_locales) == []

    # Test if form handles duplicated locales
    response = member.client.post(
        "/user/attributes/selector/",
        {
            "locales_order": commajoin(
                locale1.pk,
                locale2.pk,
                locale2.pk,
            ),
        },
    )
    assert response.status_code, 200
    assert list(User.objects.get(pk=member.user.pk).profile.sorted_locales) == [
        locale1,
        locale2,
    ]


@pytest.mark.django_db
def test_profileform_contact_email_verified(member):
    """When contact_email changes, contact_email_verified gets set to False."""
    profile = User.objects.get(pk=member.user.pk).profile
    profile.contact_email_verified = True
    profile.save()
    assert User.objects.get(pk=member.user.pk).profile.contact_email_verified is True

    params = {
        "contact_email": "contact@example.com",
    }

    response = member.client.post("/user/attributes/field/", params)
    assert response.status_code == 200
    assert User.objects.get(pk=member.user.pk).profile.contact_email_verified is False


@pytest.fixture
def mock_profile_render():
    with patch(
        "pontoon.contributors.views.render", return_value=HttpResponse("")
    ) as render:
        yield render


@pytest.mark.django_db
def test_profile_view_contributor_profile_by_username(member, mock_profile_render):
    """Users should be able to retrieve contributor's profile by its username."""
    member.client.get(f"/contributors/{member.user.username}/")

    assert mock_profile_render.call_args[0][2]["contributor"] == member.user


@pytest.mark.django_db
def test_profile_view_logged_user_profile(member, mock_profile_render):
    """Logged users should be able view their profiles"""
    member.client.get("/profile/")

    assert mock_profile_render.call_args[0][2]["contributor"] == member.user


@pytest.mark.django_db
def test_profile_view_unlogged_user_profile(member):
    """Unlogged users shouldn't have access to edit any profile."""
    member.client.logout()

    assert member.client.get("/profile/")["Location"] == "/403"


@pytest.fixture()
def contributor_translations(settings, user_a, project_a):
    """
    Setup a sample contributor with random set of translations.
    """
    translations = OrderedDict()
    for i in range(6):
        date = make_aware(datetime(2016, 12, 1) - timedelta(days=i))
        translations_count = 2
        translations.setdefault((date, translations_count), []).append(
            sorted(
                TranslationFactory.create_batch(
                    translations_count,
                    date=date,
                    user=user_a,
                    entity__resource__project=project_a,
                ),
                key=lambda t: t.pk,
                reverse=True,
            )
        )
    settings.CONTRIBUTORS_TIMELINE_EVENTS_PER_PAGE = 2
    yield translations


@pytest.mark.django_db
def test_toggle_user_profile_attribute(member):
    """Test if toggle_user_profile_attribute view works and fails as expected."""
    params = {}
    response = member.client.post("/user/attributes/toggle/", params)
    assert response.status_code == 403
    assert response.json()["message"] == "Forbidden: Attribute not allowed"

    params = {
        "attribute": "quality_checks",
    }
    response = member.client.post("/user/attributes/toggle/", params)
    assert response.status_code == 400
    assert response.json()["message"] == "Bad Request: Value not set"

    params = {
        "attribute": "quality_checks",
        "value": "false",
    }
    response = member.client.post("/user/attributes/toggle/", params)
    assert response.status_code == 200


@pytest.fixture
def mock_contributors_render():
    with patch.object(
        views.ContributorsView, "render_to_response", return_value=HttpResponse("")
    ) as mock:
        yield mock


@pytest.fixture
def mock_users_translations_counts():
    with patch("pontoon.contributors.utils.users_with_translations_counts") as mock:
        yield mock


@pytest.mark.django_db
def test_default_period(member, mock_contributors_render):
    """
    Calling the top contributors should result in period being None.
    """
    member.client.get("/contributors/")
    assert mock_contributors_render.call_args[0][0]["period"] is None


@pytest.mark.django_db
def test_invalid_period(member, mock_contributors_render):
    """
    Checks how view handles invalid period, it result in period being None - displays all data.
    """
    # If period parameter is invalid value
    member.client.get("/contributors/?period=invalidperiod")
    assert mock_contributors_render.call_args[0][0]["period"] is None

    # Period shouldn't be negative integer
    member.client.get("/contributors/?period=-6")
    assert mock_contributors_render.call_args[0][0]["period"] is None


@pytest.mark.django_db
def test_given_period(member, mock_contributors_render):
    """
    Checks if view sets and returns data for right period.
    """
    with patch(
        "django.utils.timezone.now",
        wraps=now,
        return_value=aware_datetime(2015, 7, 5),
    ):
        member.client.get("/contributors/?period=6")
        assert mock_contributors_render.call_args[0][0]["period"] == 6


@pytest.mark.django_db
def test_toggle_active_user_status(client_superuser, user_a):
    url = reverse(
        "pontoon.contributors.toggle_active_user_status", args=[user_a.username]
    )

    # request on active user --> user disabled
    assert user_a.is_active is True
    response = client_superuser.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200, User.objects.get(pk=user_a).is_active is False

    # request on disabled user --> user enabled
    response = client_superuser.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200, User.objects.get(pk=user_a).is_active is True


@pytest.mark.django_db
def test_toggle_active_user_status_user_not_found(client_superuser):
    url = reverse("pontoon.contributors.toggle_active_user_status", args=["unknown"])
    response = client_superuser.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 404


@pytest.mark.django_db
def test_toggle_active_user_status_requires_admin(member, admin, client_superuser):
    url = reverse(
        "pontoon.contributors.toggle_active_user_status", args=[member.user.username]
    )

    member.client.force_login(member.user)
    response = member.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 403

    member.client.force_login(admin)
    response = client_superuser.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200


@pytest.mark.django_db
def test_personal_access_token_generation(member):
    """Test if personal access token is generated correctly."""
    url = reverse("pontoon.contributors.generate_token")
    member.client.force_login(member.user)

    response = member.client.post(
        url, {"name": "Test Token 1"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )

    assert response.status_code == 200

    try:
        new_token_id = response.json()["data"]["new_token_id"]
        new_token_secret = response.json()["data"]["new_token_secret"]

        assert new_token_id == int(new_token_secret.split("_")[0])

    except KeyError:
        assert False, "Response does not contain 'new_token_id' or 'new_token_secret'"

    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Form submitted successfully!"
    assert response.json()["data"]["new_token_name"] == "Test Token 1"


@pytest.mark.django_db
def test_personal_access_token_deletion(member):
    """Test if personal access token is deleted correctly."""
    token = PersonalAccessToken.objects.create(
        user=member.user, name="Test Token 1", expires_at=now() + timedelta(days=30)
    )
    url = reverse("pontoon.contributors.delete_token", args=[token.id])
    member.client.force_login(member.user)

    response = member.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Token deleted successfully!"
    assert not PersonalAccessToken.objects.filter(id=token.id).exists()


@pytest.mark.django_db
def test_personal_access_token_deletion_correct_permissions(member, user_b):
    """Test if personal access token is deleted correctly."""
    token = PersonalAccessToken.objects.create(
        user=user_b, name="Test Token 1", expires_at=now() + timedelta(days=30)
    )
    url = reverse("pontoon.contributors.delete_token", args=[token.id])
    member.client.force_login(member.user)

    response = member.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    assert response.status_code == 403
    assert response.json()["status"] == "error"
    assert response.json()["message"] == "You are not authorized to delete this token."
    assert PersonalAccessToken.objects.filter(id=token.id).exists()
