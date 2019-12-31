# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_translators(apps, schema_editor):
    """
    Bug 952488 - We're assigning translation permissions to active contributors.
    """
    User = apps.get_model("auth", "User")
    users = getattr(User, "translators", getattr(User, "objects", None))

    contributors_locale = (
        users.filter(
            translation__approved=True, user_permissions__codename="can_localize"
        )
        .annotate(translated_locales=models.Count("translation__locale", distinct=True))
        .filter(translated_locales=1)
    )

    for contributor in contributors_locale:
        contributor.groups.add(
            contributor.translation_set.first().locale.translators_group
        )


def remove_translators(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Locale = apps.get_model("base", "Locale")

    UserGroup = User.groups.through
    UserGroup.objects.filter(
        group__in=Locale.objects.values_list("translators_group__pk", flat=True)
    ).delete()
    UserGroup.objects.filter(
        group__in=Locale.objects.values_list("managers_group__pk", flat=True)
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0043_create_locale_groups"),
    ]

    operations = [migrations.RunPython(create_translators, remove_translators)]
