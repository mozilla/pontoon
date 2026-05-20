from notifications.signals import notify

from django.contrib.auth.models import User
from django.db import migrations


def dedup_userprofile_usernames(apps, _):

    UserProfile = apps.get_model("base", "UserProfile")
    seen = {}
    conflicts = []

    for profile in (
        UserProfile.objects.exclude(username=None)
        .exclude(username="")
        .order_by("user__date_joined", "user_id")
    ):
        key = profile.username.lower()
        if key in seen:
            profile.username = f"{profile.username}_{profile.user_id}"
            conflicts.append(profile)
        else:
            seen[key] = profile.user_id

    UserProfile.objects.bulk_update(conflicts, ["username"])

    real_users = User.objects.in_bulk([p.user_id for p in conflicts])

    for profile in conflicts:
        user = real_users[profile.user_id]
        notify.send(
            sender=user,
            recipient=user,
            verb="",
            description=(
                f"Your Pontoon username has been updated to "
                f"<strong>{profile.username}</strong> to ensure uniqueness."
            ),
            category="direct_message",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0112_require_translation_value"),
    ]

    operations = [
        migrations.RunPython(
            code=dedup_userprofile_usernames,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
