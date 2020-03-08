# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import models, migrations


def migrate_locales_to_new_locales(apps, schema_editor):
    """Copy locales from the old ManyToMany to the new one."""
    Project = apps.get_model("base", "Project")
    ProjectLocale = apps.get_model("base", "ProjectLocale")
    for project in Project.objects.all():
        for locale in project.locales.all():
            ProjectLocale.objects.create(project=project, locale=locale)


def migrate_new_locales_to_locales(apps, schema_editor):
    """Copy locales from the new ManyToMany to the old one."""
    Project = apps.get_model("base", "Project")
    for project in Project.objects.all():
        for locale in project.new_locales.all():
            project.locales.add(locale)


def latest_activity(translation):
    """
    Return the date and user associated with the latest activity on
    this translation.
    """
    if (
        translation.approved_date is not None
        and translation.approved_date > translation.date
    ):
        return {"date": translation.approved_date, "user": translation.approved_user}
    else:
        return {"date": translation.date, "user": translation.user}


def check_latest_translation(translation, instance):
    """
    Check if the given model instance has a `latest_activity`
    attribute and, if it does, see if this translation is more
    recent than it. If so, replace it and save.
    """
    latest = instance.latest_translation
    if (
        latest is None
        or latest_activity(translation)["date"] > latest_activity(latest)["date"]
    ):
        instance.latest_translation = translation
        instance.save(update_fields=["latest_translation"])


def create_latest_translation(apps, schema_editor):
    """
    Populate the latest_translation fields by searching the existing
    translations.
    """
    Stats = apps.get_model("base", "Stats")
    ProjectLocale = apps.get_model("base", "ProjectLocale")
    Translation = apps.get_model("base", "Translation")
    for stats in Stats.objects.all():
        project = stats.resource.project
        locale = stats.locale
        path = stats.resource.path
        translations = Translation.objects.filter(
            entity__resource__project=project,
            entity__resource__path=path,
            locale=locale,
        )

        if not translations.exists():
            continue
        latest_creation = translations.order_by("-date")[0]
        approvals = translations.filter(approved_date__isnull=False).order_by(
            "-approved_date"
        )

        # Choose whether the latest creation or latest approval is the
        # latest translation.
        if not approvals.exists():
            stats.latest_translation = latest_creation
        else:
            latest_approval = approvals[0]
            if (
                latest_approval.approved_date
                and latest_creation.date < latest_approval.approved_date
            ):
                stats.latest_translation = latest_approval
            else:
                stats.latest_translation = latest_creation

        # Update the project and locale as well.
        stats.save(update_fields=["latest_translation"])
        check_latest_translation(stats.latest_translation, project)
        check_latest_translation(stats.latest_translation, locale)

        try:
            project_locale = ProjectLocale.objects.get(project=project, locale=locale)
            check_latest_translation(stats.latest_translation, project_locale)
        except ProjectLocale.DoesNotExist:
            pass


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0037_entity_resource_related_names"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectLocale",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "latest_translation",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="base.Translation",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="locale",
            name="latest_translation",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="base.Translation",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="latest_translation",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="base.Translation",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="stats",
            name="latest_translation",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="base.Translation",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="projectlocale",
            name="locale",
            field=models.ForeignKey(to="base.Locale"),
        ),
        migrations.AddField(
            model_name="projectlocale",
            name="project",
            field=models.ForeignKey(to="base.Project"),
        ),
        migrations.AddField(
            model_name="project",
            name="new_locales",
            field=models.ManyToManyField(
                related_name="+", through="base.ProjectLocale", to="base.Locale"
            ),
        ),
        migrations.RunPython(
            migrate_locales_to_new_locales,
            migrate_new_locales_to_locales,
            elidable=True,
        ),
        migrations.RemoveField(model_name="project", name="locales",),
        migrations.RemoveField(model_name="project", name="new_locales",),
        migrations.AddField(
            model_name="project",
            name="locales",
            field=models.ManyToManyField(
                to="base.Locale", through="base.ProjectLocale"
            ),
        ),
        migrations.RunPython(create_latest_translation, noop, elidable=True),
    ]
