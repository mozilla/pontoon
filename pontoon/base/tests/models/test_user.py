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
