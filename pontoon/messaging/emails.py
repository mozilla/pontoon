import datetime
import logging

from collections import defaultdict

from notifications.models import Notification

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone

from pontoon.messaging.utils import html_to_plain_text_with_links


log = logging.getLogger(__name__)


def send_notification_digest(frequency="Daily"):
    """
    Sends notification email digests to users based on the specified frequency (Daily or Weekly).
    """
    log.info(f"Start sending { frequency } notification email digests.")

    if frequency == "Daily":
        start_time = timezone.now() - datetime.timedelta(days=1)
    elif frequency == "Weekly":
        start_time = timezone.now() - datetime.timedelta(weeks=1)

    users = (
        User.objects
        # Users with the selected notification email frequency
        .filter(profile__notification_email_frequency=frequency)
        # Users subscribed to at least one email notification type
        .filter(
            Q(profile__new_string_notifications_email=True)
            | Q(profile__project_deadline_notifications_email=True)
            | Q(profile__comment_notifications_email=True)
            | Q(profile__unreviewed_suggestion_notifications_email=True)
            | Q(profile__review_notifications_email=True)
            | Q(profile__new_contributor_notifications_email=True)
        )
    )

    notifications = Notification.objects.filter(
        recipient__in=users,
        timestamp__gte=start_time,
    ).select_related("recipient__profile")

    # Group notifications by user
    notifications_map = defaultdict(list)
    for notification in notifications:
        recipient = notification.recipient

        # Only include notifications the user chose to receive via email
        if recipient.is_subscribed_to_notification(notification):
            notifications_map[recipient].append(notification)

    subject = f"{frequency} notifications summary"
    template = get_template("messaging/emails/notification_digest.html")

    # Process and send email for each user
    for user, user_notifications in notifications_map.items():
        body_html = template.render(
            {
                "notifications": user_notifications,
                "subject": subject,
            }
        )
        body_text = html_to_plain_text_with_links(body_html)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    recipient_count = len(notifications_map.keys())

    log.info(f"Notification email digests sent to {recipient_count} users.")
