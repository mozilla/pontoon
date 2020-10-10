from __future__ import absolute_import

from collections import OrderedDict
from datetime import (
    datetime,
    timedelta,
)
from mock import patch
from random import randint
from six.moves import range

from django.http import HttpResponse
from django.urls import reverse
from django.utils.timezone import now, make_aware
from pytest_django.asserts import assertContains

from pontoon.base.models import User
from pontoon.base.tests import (
    LocaleFactory,
    ProjectFactory,
    TranslationFactory,
    TestCase,
    UserFactory,
)
from pontoon.base.tests.test_views import UserTestCase
from pontoon.base.utils import aware_datetime
from pontoon.contributors import views


def commajoin(*items):
    """
    Small helper function that joins all items by comma and maps types
    of items into strings.
    """
    return ",".join(map(str, items))


class ContributorProfileTests(UserTestCase):
    """Tests related to the saving user profile."""

    url = reverse("pontoon.contributors.settings")

    def test_invalid_first_name(self):
        response = self.client.post(self.url, {"first_name": '<aa>"\'"'})

        assertContains(response, "Enter a valid value.")

    def test_invalid_email(self):
        response = self.client.post(self.url, {"email": "usermail"})

        assertContains(response, "Enter a valid email address.")

    def test_missing_profile_fields(self):
        response = self.client.post(self.url, {})

        assertContains(response, "This field is required.", count=2)

    def test_valid_first_name(self):
        response = self.client.post(
            self.url, {"first_name": "contributor", "email": self.user.email}
        )

        assertContains(response, "Settings saved.")

    def test_user_locales_order(self):
        locale1, locale2, locale3 = LocaleFactory.create_batch(3)
        response = self.client.get(self.url)
        assert response.status_code == 200

        response = self.client.post(
            "/settings/",
            {
                "first_name": "contributor",
                "email": self.user.email,
                "locales_order": commajoin(locale2.pk, locale1.pk, locale3.pk,),
            },
        )

        assert response.status_code == 200
        assert list(User.objects.get(pk=self.user.pk).profile.sorted_locales) == [
            locale2,
            locale1,
            locale3,
        ]
        # Test if you can clear all locales
        response = self.client.post(
            "/settings/",
            {
                "first_name": "contributor",
                "email": self.user.email,
                "locales_order": "",
            },
        )
        assert response.status_code == 200
        assert list(User.objects.get(pk=self.user.pk).profile.sorted_locales) == []

        # Test if form handles duplicated locales
        response = self.client.post(
            "/settings/",
            {
                "first_name": "contributor",
                "email": self.user.email,
                "locales_order": commajoin(locale1.pk, locale2.pk, locale2.pk,),
            },
        )
        assert response.status_code, 200
        assert list(User.objects.get(pk=self.user.pk).profile.sorted_locales) == [
            locale1,
            locale2,
        ]


class ContributorProfileViewTests(UserTestCase):
    def setUp(self):
        super(ContributorProfileViewTests, self).setUp()

        mock_render = patch(
            "pontoon.contributors.views.render", return_value=HttpResponse("")
        )
        self.mock_render = mock_render.start()
        self.addCleanup(mock_render.stop)

    def test_contributor_profile_by_username(self):
        """Users should be able to retrieve contributor's profile by its username."""
        self.client.get("/contributors/{}/".format(self.user.username))

        assert self.mock_render.call_args[0][2]["contributor"] == self.user

    def test_contributor_profile_by_email(self):
        """Check if we can access contributor profile by its email."""
        self.client.get("/contributors/{}/".format(self.user.email))

        assert self.mock_render.call_args[0][2]["contributor"] == self.user

    def test_logged_user_profile(self):
        """Logged user should be able to re"""
        self.client.get("/profile/")

        assert self.mock_render.call_args[0][2]["contributor"] == self.user

    def test_unlogged_user_profile(self):
        """Unlogged users shouldn't have access to edit any profile."""
        self.client.logout()

        assert self.client.get("/profile/")["Location"] == "/403"


class ContributorTimelineViewTests(UserTestCase):
    """User timeline is a list of events created by a certain contributor."""

    def setUp(self):
        """
        We setup a sample contributor with random set of translations.
        """
        super(ContributorTimelineViewTests, self).setUp()
        self.project = ProjectFactory.create()
        self.translations = OrderedDict()

        for i in range(26):
            date = make_aware(datetime(2016, 12, 1) - timedelta(days=i))
            translations_count = randint(1, 3)
            self.translations.setdefault((date, translations_count), []).append(
                sorted(
                    TranslationFactory.create_batch(
                        translations_count,
                        date=date,
                        user=self.user,
                        entity__resource__project=self.project,
                    ),
                    key=lambda t: t.pk,
                    reverse=True,
                )
            )

        mock_render = patch(
            "pontoon.contributors.views.render", return_value=HttpResponse("")
        )
        self.mock_render = mock_render.start()
        self.addCleanup(mock_render.stop)

    def test_timeline(self):
        """Backend should return events filtered by page number requested by user."""
        self.client.get("/contributors/{}/timeline/?page=2".format(self.user.username))

        assert self.mock_render.call_args[0][2]["events"] == [
            {
                "date": dt,
                "type": "translation",
                "count": count,
                "project": self.project,
                "translation": translations[0][0],
            }
            for (dt, count), translations in list(self.translations.items())[10:20]
        ]

    def test_timeline_invalid_page(self):
        """Backend should return 404 error when user requests an invalid/empty page."""
        response = self.client.get(
            "/contributors/{}/timeline/?page=45".format(self.user.username)
        )
        assert response.status_code == 404

        response = self.client.get(
            "/contributors/{}/timeline/?page=-aa45".format(self.user.username)
        )
        assert response.status_code == 404

    def test_non_active_contributor(self):
        """Test if backend is able return events for a user without contributions."""
        nonactive_contributor = UserFactory.create()
        self.client.get(
            "/contributors/{}/timeline/".format(nonactive_contributor.username)
        )
        assert self.mock_render.call_args[0][2]["events"] == [
            {"date": nonactive_contributor.date_joined, "type": "join"}
        ]

    def test_timeline_join(self):
        """Last page of results should include informations about the when user joined pontoon."""
        self.client.get("/contributors/{}/timeline/?page=3".format(self.user.username))

        assert self.mock_render.call_args[0][2]["events"][-1] == {
            "date": self.user.date_joined,
            "type": "join",
        }


class ContributorsTests(TestCase):
    def setUp(self):
        mock_render = patch.object(
            views.ContributorsView, "render_to_response", return_value=HttpResponse("")
        )
        self.mock_render = mock_render.start()
        self.addCleanup(mock_render.stop)

        mock_users_with_translations_counts = patch(
            "pontoon.contributors.views.users_with_translations_counts"
        )
        self.mock_users_with_translations_counts = (
            mock_users_with_translations_counts.start()
        )
        self.addCleanup(mock_users_with_translations_counts.stop)

    def test_default_period(self):
        """
        Calling the top contributors should result in period being None.
        """
        self.client.get("/contributors/")
        assert self.mock_render.call_args[0][0]["period"] is None
        assert self.mock_users_with_translations_counts.call_args[0][0] is None

    def test_invalid_period(self):
        """
        Checks how view handles invalid period, it result in period being None - displays all data.
        """
        # If period parameter is invalid value
        self.client.get("/contributors/?period=invalidperiod")
        assert self.mock_render.call_args[0][0]["period"] is None
        assert self.mock_users_with_translations_counts.call_args[0][0] is None

        # Period shouldn't be negative integer
        self.client.get("/contributors/?period=-6")
        assert self.mock_render.call_args[0][0]["period"] is None
        assert self.mock_users_with_translations_counts.call_args[0][0] is None

    def test_given_period(self):
        """
        Checks if view sets and returns data for right period.
        """
        with patch(
            "django.utils.timezone.now",
            wraps=now,
            return_value=aware_datetime(2015, 7, 5),
        ):
            self.client.get("/contributors/?period=6")
            assert self.mock_render.call_args[0][0]["period"] == 6
            assert self.mock_users_with_translations_counts.call_args[0][
                0
            ] == aware_datetime(2015, 1, 5)
