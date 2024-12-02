import re

from django.db import migrations


def get_category(notification):
    verb = notification.verb
    desc = notification.description

    # New strings notifications
    if re.match(r"updated with \d+ new strings", verb):
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

    if re.match(r"has reviewed suggestions", verb):
        # Review actions on own suggestions notifications
        if desc.startswith("Your suggestions have been reviewed"):
            return "review"

        # New team contributors notifications
        if desc.startswith("<a href="):
            return "new_contributor"


def store_notification_categories(apps, schema_editor):
    Notification = apps.get_model("notifications", "Notification")
    notifications = Notification.objects.filter(data__isnull=True)

    for notification in notifications:
        category = get_category(notification)

        if category:
            notification.data = {"category": category}

    Notification.objects.bulk_update(notifications, ["data"], batch_size=2000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0068_userprofile_notification_emails"),
    ]

    operations = [
        migrations.RunPython(
            code=store_notification_categories,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
