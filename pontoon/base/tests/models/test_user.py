from collections import defaultdict

import pytest

from notifications.models import Notification

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
def test_user_status(user_a, user_b, user_c, user_d, gt_user, locale_a, project_a):
    project_contact = user_d

    # New User
    assert user_a.status(locale_a, project_contact)[1] == "New User"

    # Fake user object
    imported = User(username="Imported")
    assert imported.status(locale_a, project_contact)[1] == ""

    # Admin
    user_a.is_superuser = True
    assert user_a.status(locale_a, project_contact)[1] == "Admin"

    # Manager
    locale_a.managers_group.user_set.add(user_b)
    assert user_b.status(locale_a, project_contact)[1] == "Team Manager"

    # Translator
    locale_a.translators_group.user_set.add(user_c)
    assert user_c.status(locale_a, project_contact)[1] == "Translator"

    # PM
    assert user_d.status(locale_a, project_contact)[1] == "Project Manager"

    # System user (Google Translate)
    project_contact = gt_user
    assert gt_user.status(locale_a, project_contact)[1] == ""


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
    "verb, description, expected",
    [
        # New strings notifications
        ("updated with 5 new strings", "", True),
        ("updated with 0 new strings", "", True),
        # Project target dates notifications
        ("due in 7 days", "", True),
        ("due in 14 days", "", True),
        # Comments notifications
        ("has pinned a comment in", "", False),
        ("has added a comment in", "", False),
        # New suggestions ready for review notifications
        ("", "", True),
        # Review actions on own suggestions notifications
        ("has reviewed suggestions", "Your suggestions have been reviewed", False),
        # New team contributors notifications
        (
            "has reviewed suggestions",
            '<a href="https://example.com">New Contributor</a>',
            True,
        ),
        # Fallback case
        ("unknown notification type", "Unknown description", False),
    ],
)
def test_is_subscribed_to_notification(
    user_with_subscriptions, verb, description, expected
):
    # Create a notification object
    notification = Notification(verb=verb, description=description)

    # Call the function and assert the result
    assert (
        user_with_subscriptions.is_subscribed_to_notification(notification) == expected
    )
