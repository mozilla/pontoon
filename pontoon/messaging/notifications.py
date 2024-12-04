from notifications.signals import notify

from django.template.loader import render_to_string


def send_badge_notification(user, badge, level):
    desc = render_to_string(
        "messaging/badge_notification.html",
        {"badge": badge, "level": level, "user": user},
    )
    notify.send(
        sender=user,
        recipient=user,
        verb="ignore",  # Triggers render of description only
        description=desc,
        category="badge",
    )
