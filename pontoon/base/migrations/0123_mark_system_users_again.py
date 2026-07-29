from django.db import migrations


# Both variants are matched, because this migration is not guaranteed to run
# after the @mozilla.com -> @example.com rename in
# insights.0017_fix_projectlocale_insights_again.
system_user_emails = [
    "pontoon-sync@example.com",
    "pontoon-gt@example.com",
    "pontoon-tm@example.com",
    "pontoon-sync@mozilla.com",
    "pontoon-gt@mozilla.com",
    "pontoon-tm@mozilla.com",
]


def mark_system_users(apps, schema_editor):
    """Mark system users missed by base.0039_mark_system_users.

    The sync user is created by sync.0002_change_pontoon_sync_email, which has no
    dependency ordering it before base.0039_mark_system_users. On a fresh install
    the base migrations run first, so 0039 finds no sync user to mark and the
    account is left with system_user=False.
    """
    UserProfile = apps.get_model("base", "UserProfile")
    UserProfile.objects.filter(user__email__in=system_user_emails).update(
        system_user=True
    )


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0122_reparse_multi_pattern_fluent"),
        # Ensures the sync user exists before we try to mark it.
        ("sync", "0002_change_pontoon_sync_email"),
    ]

    operations = [
        migrations.RunPython(
            code=mark_system_users,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
