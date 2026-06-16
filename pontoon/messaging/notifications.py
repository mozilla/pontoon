from notifications.signals import notify

from django.template.loader import render_to_string


def send_notification(sender, recipient, **kwargs):
    """Send a notification, skipping system users (e.g. pontoon-sync, pontoon-gt, pontoon-tm)."""
    if recipient.profile.system_user:
        return
    notify.send(sender, recipient=recipient, **kwargs)


def send_badge_notification(user, badge, level):
    desc = render_to_string(
        "messaging/notifications/badge_notification.html",
        {"badge": badge, "level": level, "user": user},
    )
    send_notification(
        user,
        recipient=user,
        verb="ignore",  # Triggers render of description only
        description=desc,
        category="badge",
    )
