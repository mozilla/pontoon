import random
import string

from django.db import migrations


def dedup_userprofile_usernames(apps, _):

    UserProfile = apps.get_model("base", "UserProfile")
    seen = {}
    conflicts = []

    for profile in (
        UserProfile.objects.exclude(username=None)
        .exclude(username="")
        .order_by("user_id")
    ):
        key = profile.username.lower()
        random_key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        if key in seen:
            profile.username = f"{profile.username}_{random_key}"
            conflicts.append(profile)
        else:
            seen[key] = profile.user_id


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0113_userbanlog"),
    ]

    operations = [
        migrations.RunPython(
            code=dedup_userprofile_usernames,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
