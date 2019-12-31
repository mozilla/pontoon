# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-22 13:06
from __future__ import unicode_literals

from django.db import migrations

USERS = [
    ("pontoon-tm@mozilla.com", "translation-memory", "Translation Memory"),
    ("pontoon-gt@mozilla.com", "google-translate", "Google Translate"),
]


def add_pretranslation_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("base", "UserProfile")

    users = User.objects.bulk_create(
        [
            User(email=email, username=username, first_name=name,)
            for email, username, name in USERS
        ]
    )

    UserProfile.objects.bulk_create([UserProfile(user=user) for user in users])


def remove_pretranslation_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("base", "UserProfile")

    users = User.objects.filter(email__in=[u[0] for u in USERS])
    user_profiles = UserProfile.objects.filter(user__in=users)
    user_profiles.delete()
    users.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0145_project_pretranslate"),
    ]

    operations = [
        migrations.RunPython(add_pretranslation_users, remove_pretranslation_users,),
    ]
