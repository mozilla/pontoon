from collections import OrderedDict
from datetime import (
    datetime,
    timedelta,
)
from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.urls import reverse
from django.utils.timezone import now, make_aware

from pontoon.base.models import User
from pontoon.base.tests import (
    LocaleFactory,
    TranslationFactory,
    UserFactory,
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
def test_profileform_invalid_first_name(member, settings_url):
    response = member.client.post(settings_url, {"first_name": '<aa>"\'"'})

    assert b"Enter a valid value." in response.content


@pytest.mark.django_db
def test_profileform_invalid_email(member, settings_url):
    response = member.client.post(settings_url, {"email": "usermail"})

    assert b"Enter a valid email address." in response.content


@pytest.mark.django_db
def test_profileform_missing_profile_fields(member, settings_url):
    response = member.client.post(settings_url, {})

    assert response.content.count(b"This field is required.") == 2


@pytest.mark.django_db
def test_profileform_valid_first_name(member, settings_url):
    response = member.client.post(
        settings_url, {"first_name": "contributor", "email": member.user.email}
    )

    assert b"Settings saved." in response.content


@pytest.mark.django_db
def test_profileform_user_locales_order(member, settings_url):
    locale1, locale2, locale3 = LocaleFactory.create_batch(3)
    response = member.client.get(settings_url)
    assert response.status_code == 200

    response = member.client.post(
        "/settings/",
        {
            "first_name": "contributor",
            "email": member.user.email,
            "locales_order": commajoin(locale2.pk, locale1.pk, locale3.pk,),
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
        "/settings/",
        {"first_name": "contributor", "email": member.user.email, "locales_order": ""},
    )
    assert response.status_code == 200
    assert list(User.objects.get(pk=member.user.pk).profile.sorted_locales) == []

    # Test if form handles duplicated locales
    response = member.client.post(
        "/settings/",
        {
            "first_name": "contributor",
            "email": member.user.email,
            "locales_order": commajoin(locale1.pk, locale2.pk, locale2.pk,),
        },
    )
    assert response.status_code, 200
    assert list(User.objects.get(pk=member.user.pk).profile.sorted_locales) == [
        locale1,
        locale2,
    ]


@pytest.fixture
def mock_profile_render():
    with patch(
        "pontoon.contributors.views.render", return_value=HttpResponse("")
    ) as render:
        yield render


@pytest.mark.django_db
def test_profile_view_contributor_profile_by_username(member, mock_profile_render):
    """Users should be able to retrieve contributor's profile by its username."""
    member.client.get("/contributors/{}/".format(member.user.username))

    assert mock_profile_render.call_args[0][2]["contributor"] == member.user


@pytest.mark.django_db
def test_profile_view_contributor_profile_by_email(member, mock_profile_render):
    """Check if we can access contributor profile by its email."""
    member.client.get("/contributors/{}/".format(member.user.email))

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
def test_timeline(
    contributor_translations, client, project_a, mock_profile_render, user_a
):
    """Backend should return events filtered by page number requested by user."""
    client.get("/contributors/{}/timeline/?page=2".format(user_a.username))
    assert mock_profile_render.call_args[0][2]["events"] == [
        {
            "date": dt,
            "type": "translation",
            "count": count,
            "project": project_a,
            "translation": translations[0][0],
        }
        for (dt, count), translations in list(contributor_translations.items())[2:4]
    ]


@pytest.mark.django_db
def test_timeline_invalid_page(contributor_translations, client, user_a):
    """Backend should return 404 error when user requests an invalid/empty page."""
    response = client.get("/contributors/{}/timeline/?page=45".format(user_a.username))
    assert response.status_code == 404

    response = client.get(
        "/contributors/{}/timeline/?page=-aa45".format(user_a.username)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_timeline_non_active_contributor(
    contributor_translations, client, mock_profile_render
):
    """Test if backend is able return events for a user without contributions."""
    nonactive_contributor = UserFactory.create()
    client.get("/contributors/{}/timeline/".format(nonactive_contributor.username))
    assert mock_profile_render.call_args[0][2]["events"] == [
        {"date": nonactive_contributor.date_joined, "type": "join"}
    ]


@pytest.mark.django_db
def test_timeline_join(client, contributor_translations, mock_profile_render, user_a):
    """Last page of results should include informations about the when user joined pontoon."""
    client.get("/contributors/{}/timeline/?page=3".format(user_a.username))

    assert mock_profile_render.call_args[0][2]["events"][-1] == {
        "date": user_a.date_joined,
        "type": "join",
    }


@pytest.fixture
def mock_contributors_render():
    with patch.object(
        views.ContributorsView, "render_to_response", return_value=HttpResponse("")
    ) as mock:
        yield mock


@pytest.fixture
def mock_users_translations_counts():
    with patch("pontoon.contributors.views.users_with_translations_counts") as mock:
        yield mock


@pytest.mark.django_db
def test_default_period(
    member, mock_contributors_render, mock_users_translations_counts
):
    """
    Calling the top contributors should result in period being None.
    """
    member.client.get("/contributors/")
    assert mock_contributors_render.call_args[0][0]["period"] is None
    assert mock_users_translations_counts.call_args[0][0] is None


@pytest.mark.django_db
def test_invalid_period(
    member, mock_contributors_render, mock_users_translations_counts
):
    """
    Checks how view handles invalid period, it result in period being None - displays all data.
    """
    # If period parameter is invalid value
    member.client.get("/contributors/?period=invalidperiod")
    assert mock_contributors_render.call_args[0][0]["period"] is None
    assert mock_users_translations_counts.call_args[0][0] is None

    # Period shouldn't be negative integer
    member.client.get("/contributors/?period=-6")
    assert mock_contributors_render.call_args[0][0]["period"] is None
    assert mock_users_translations_counts.call_args[0][0] is None


@pytest.mark.django_db
def test_given_period(member, mock_contributors_render, mock_users_translations_counts):
    """
    Checks if view sets and returns data for right period.
    """
    with patch(
        "django.utils.timezone.now", wraps=now, return_value=aware_datetime(2015, 7, 5),
    ):
        member.client.get("/contributors/?period=6")
        assert mock_contributors_render.call_args[0][0]["period"] == 6
        assert mock_users_translations_counts.call_args[0][0] == aware_datetime(
            2015, 1, 5
        )
