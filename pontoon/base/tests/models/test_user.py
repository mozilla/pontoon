from collections import defaultdict

import pytest

from allauth.socialaccount.models import SocialAccount
from notifications.models import Notification
from notifications.signals import notify

from django.contrib.auth.models import User


@pytest.mark.django_db
def test_user_role(user_a, user_b, user_c, locale_a):
    # Default role
    assert user_a.role() == "Contributor"

    # Superuser
    user_a.is_superuser = True
    assert user_a.role() == "Admin"

    # Fake user object
    imported = User(username="Imported")
    assert imported.role() == "System User"

    # System user
    user_b.profile.system_user = True
    assert user_b.role() == "System User"

    # Translator
    translators = defaultdict(set)
    translators[user_c].add(locale_a.code)
    assert user_c.role(translators=translators) == f"Translator for {locale_a.code}"

    # Manager
    managers = defaultdict(set)
    managers[user_c].add(locale_a.code)
    assert user_c.role(managers=managers) == f"Manager for {locale_a.code}"


@pytest.mark.django_db
def test_user_locale_role(user_a, user_b, user_c, locale_a):
    # Default role
    assert user_a.locale_role(locale_a) == "Contributor"

    # Superuser
    user_a.is_superuser = True
    assert user_a.locale_role(locale_a) == "Admin"

    # Fake user object
    imported = User(username="Imported")
    assert imported.locale_role(locale_a) == "System User"

    # System user
    user_b.profile.system_user = True
    assert user_b.locale_role(locale_a) == "System User"

    # Translator
    locale_a.translators_group.user_set.add(user_c)
    assert user_c.locale_role(locale_a) == "Translator"

    # Manager
    locale_a.managers_group.user_set.add(user_c)
    assert user_c.locale_role(locale_a) == "Manager"

    # Admin and Manager
    locale_a.managers_group.user_set.add(user_a)
    assert user_a.locale_role(locale_a) == "Manager"


@pytest.mark.django_db
def test_user_banner(user_a, user_b, user_c, user_d, gt_user, locale_a, project_a):
    project_contact = user_d

    # New User
    assert user_a.banner(locale_a, project_contact)[1] == "New User"

    # Fake user object
    imported = User(username="Imported")
    assert imported.banner(locale_a, project_contact)[1] == ""

    # Admin
    user_a.is_superuser = True
    assert user_a.banner(locale_a, project_contact)[1] == "Admin"

    # Manager
    locale_a.managers_group.user_set.add(user_b)
    assert user_b.banner(locale_a, project_contact)[1] == "Team Manager"

    # Translator
    locale_a.translators_group.user_set.add(user_c)
    assert user_c.banner(locale_a, project_contact)[1] == "Translator"

    # PM
    assert user_d.banner(locale_a, project_contact)[1] == "Project Manager"

    # System user (Google Translate)
    project_contact = gt_user
    assert gt_user.banner(locale_a, project_contact)[1] == ""


@pytest.fixture
def user_with_subscriptions():
    """Fixture for a User with notification subscriptions."""
    user = User.objects.create(username="subscriber")
    user.profile.new_string_notifications_email = True
    user.profile.project_deadline_notifications_email = True
    user.profile.comment_notifications_email = False
    user.profile.unreviewed_suggestion_notifications_email = True
    user.profile.review_notifications_email = False
    user.profile.new_contributor_notifications_email = True
    user.profile.save()
    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "category, expected",
    [
        # New strings notifications
        ("new_string", True),
        # Project target dates notifications
        ("project_deadline", True),
        # Comments notifications
        ("comment", False),
        # New suggestions ready for review notifications
        ("unreviewed_suggestion", True),
        # Review actions on own suggestions notifications
        ("review", False),
        # New team contributors notifications
        ("new_contributor", True),
        # Notification send directly from the Messaging Center
        ("direct_message", True),
        # Fallback case
        ("unknown", False),
    ],
)
def test_is_subscribed_to_notification(user_with_subscriptions, category, expected):
    # Create a notification object
    notification = Notification(data={"category": category})

    # Call the function and assert the result
    assert (
        user_with_subscriptions.is_subscribed_to_notification(notification) == expected
    )


@pytest.mark.django_db
def test_is_subscribed_to_notification_no_data(user_with_subscriptions):
    # Create a notification object without a data attribute
    notification = Notification()

    # Call the function and assert the result
    assert user_with_subscriptions.is_subscribed_to_notification(notification) is False


@pytest.mark.django_db
def test_is_subscribed_to_notification_no_category(user_with_subscriptions):
    # Create a notification object without a category key in data
    notification = Notification(data={"something": None})

    # Call the function and assert the result
    assert user_with_subscriptions.is_subscribed_to_notification(notification) is False


@pytest.mark.django_db
def test_serialized_notifications_new_string_created_time(user_a, project_a):
    """
    New string notifications carrying a created_time on their data link to the
    exact batch of added strings via the created_time URL filter.
    """
    notify.send(
        sender=project_a,
        recipient=user_a,
        verb="updated with 3 new strings",
        category="new_string",
        created_time="202605240444",
    )

    notification = user_a.serialized_notifications["notifications"][0]
    assert notification["actor"]["url"] == (
        f"/projects/{project_a.slug}/all-resources/"
        "?created_time=202605240444-202605240444"
    )


@pytest.mark.django_db
def test_serialized_notifications_new_string_without_created_time(user_a, project_a):
    """
    Older new string notifications without a created_time fall back to linking
    to all missing and pretranslated strings.
    """
    notify.send(
        sender=project_a,
        recipient=user_a,
        verb="updated with 3 new strings",
        category="new_string",
    )

    notification = user_a.serialized_notifications["notifications"][0]
    assert notification["actor"]["url"] == (
        f"/projects/{project_a.slug}/all-resources/?status=missing,pretranslated"
    )


@pytest.mark.django_db
def test_gravatar_url_returns_fxa_avatar_when_linked(user_a):
    SocialAccount.objects.create(
        user=user_a,
        provider="fxa",
        uid="1234",
        extra_data={"avatar": "https://profile.accounts.firefox.com/v1/avatar/abc"},
    )
    assert user_a.avatar_url(88) == "https://profile.accounts.firefox.com/v1/avatar/abc"


@pytest.mark.django_db
def test_gravatar_url_falls_back_to_gravatar_when_no_fxa(user_a):
    url = user_a.avatar_url(88)
    assert "gravatar.com/avatar/" in url


@pytest.mark.django_db
def test_gravatar_url_falls_back_to_gravatar_when_fxa_has_no_avatar(user_a):
    SocialAccount.objects.create(
        user=user_a,
        provider="fxa",
        uid="1234",
        extra_data={},
    )
    url = user_a.avatar_url(88)
    assert "gravatar.com/avatar/" in url
