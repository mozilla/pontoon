import logging
import re

from django.db import migrations


log = logging.getLogger(__name__)


def get_category(notification):
    verb = notification.verb
    desc = notification.description

    # New strings notifications
    if re.match(r"updated with \d+ new string", verb):
        return "new_string"

    # Project target dates notifications
    if re.match(r"due in \d+ days", verb):
        return "project_deadline"

    # Comments notifications
    if re.match(r"has (pinned|added) a comment in", verb):
        return "comment"

    # New suggestions ready for review notifications
    if verb == "":
        return "unreviewed_suggestion"

    if verb == "has reviewed suggestions":
        # Review actions on own suggestions notifications
        if desc.startswith("Your suggestions have been reviewed"):
            return "review"

        # New team contributors notifications
        if "has made their first contribution to" in desc:
            return "new_contributor"

    if verb == "has sent a message in" or verb == "has sent you a message":
        return "direct_message"

    return None


def store_notification_categories(apps, schema_editor):
    Notification = apps.get_model("notifications", "Notification")
    notifications = Notification.objects.all()
    unchanged = []

    for notification in notifications:
        category = get_category(notification)

        if category == "direct_message":
            notification.data["category"] = category
        elif category:
            notification.data = {"category": category}
        else:
            unchanged.append(notification)

    Notification.objects.bulk_update(notifications, ["data"], batch_size=2000)

    log.info(f"Notifications categorized: {len(notifications) - len(unchanged)}.")
    log.info(f"Notifications left unchanged: {len(unchanged)}.")


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0068_userprofile_notification_emails"),
        ("notifications", "0009_alter_notification_options_and_more"),
    ]

    operations = [
        migrations.RunPython(
            code=store_notification_categories,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
