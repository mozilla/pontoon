# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bulk_update.helper import bulk_update

from django.db import migrations
from django.db.models import Sum


def aggregate(stats, instance):
    aggregated = stats.aggregate(
        total=Sum("resource__entity_count"),
        approved=Sum("approved_count"),
        translated=Sum("translated_count"),
        fuzzy=Sum("fuzzy_count"),
    )

    instance.total_strings = aggregated["total"]
    instance.approved_strings = aggregated["approved"]
    instance.translated_strings = aggregated["translated"]
    instance.fuzzy_strings = aggregated["fuzzy"]

    return instance


def populate_stats(apps, schema_editor):
    Stats = apps.get_model("base", "Stats")
    Project = apps.get_model("base", "Project")
    Locale = apps.get_model("base", "Locale")
    ProjectLocale = apps.get_model("base", "ProjectLocale")

    # Projects
    projects = Project.objects.all()
    for project in projects:
        stats = Stats.objects.filter(
            resource__project=project, resource__entities__obsolete=False,
        ).distinct()

        if stats:
            project = aggregate(stats, project)

    if projects:
        bulk_update(projects)

    # Locales
    locales = Locale.objects.filter(stats__isnull=False).distinct()
    for locale in locales:
        stats = Stats.objects.filter(
            resource__project__disabled=False,
            resource__entities__obsolete=False,
            locale=locale,
        ).distinct()

        if stats:
            locale = aggregate(stats, locale)

    if locales:
        bulk_update(locales)

    # Project-Locales
    project_locales = ProjectLocale.objects.all()
    for project_locale in project_locales:
        stats = Stats.objects.filter(
            resource__project=project_locale.project,
            resource__project__disabled=False,
            resource__entities__obsolete=False,
            locale=project_locale.locale,
        ).distinct()

        if stats:
            project_locale = aggregate(stats, project_locale)

    if project_locales:
        bulk_update(project_locales)


def remove_stats(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0054_rename_stats"),
    ]

    operations = [
        migrations.RunPython(populate_stats, remove_stats, elidable=True),
    ]
