import pytest

from notifications.models import Notification
from notifications.signals import notify

from pontoon.base.models.user import User
from pontoon.base.notification_utils import (
    is_subscribed_to_notification,
    serialized_notifications,
)


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

    assert (
        is_subscribed_to_notification(user_with_subscriptions, notification) is expected
    )


@pytest.mark.django_db
def test_is_subscribed_to_notification_no_data(user_with_subscriptions):
    # Create a notification object without a data attribute
    notification = Notification()

    assert is_subscribed_to_notification(user_with_subscriptions, notification) is False


@pytest.mark.django_db
def test_is_subscribed_to_notification_no_category(user_with_subscriptions):
    # Create a notification object without a category key in data
    notification = Notification(data={"something": None})

    assert is_subscribed_to_notification(user_with_subscriptions, notification) is False


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

    notification = serialized_notifications(user_a)["notifications"][0]
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

    notification = serialized_notifications(user_a)["notifications"][0]
    assert notification["actor"]["url"] == (
        f"/projects/{project_a.slug}/all-resources/?status=missing,pretranslated"
    )


@pytest.mark.django_db
def test_serialized_notifications_date_format(user_a, project_a):
    """
    The serialized "date" carries the exact date and time shown in the
    timestamp tooltip, matching format_datetime("full") used by the Django
    notifications menu.
    """
    from pontoon.base.templatetags.helpers import format_datetime

    notify.send(
        sender=project_a,
        recipient=user_a,
        verb="has reviewed suggestions",
    )

    notification_obj = Notification.objects.get(recipient=user_a)
    serialized = serialized_notifications(user_a)["notifications"][0]
    assert serialized["date"] == format_datetime(notification_obj.timestamp, "full")
    assert serialized["date_iso"] == notification_obj.timestamp.isoformat()
