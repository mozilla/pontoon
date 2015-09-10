# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def copy_repo_attributes_to_relation(apps, schema_editor):
    """
    Copy data in Project.repository_* attributes to Repository
    instances.
    """
    Project = apps.get_model('base', 'Project')
    Repository = apps.get_model('base', 'Repository')
    for project in Project.objects.all():
        repo = Repository(
            project=project,
            type=project.repository_type,
            url=project.repository_url,
        )
        repo.save()


def copy_relation_to_repo_attributes(apps, schema_editor):
    """
    Copy data in Repository instances to Project.repository_*
    attributes.
    """
    Project = apps.get_model('base', 'Project')
    for project in Project.objects.all():
        repo = project.repository_set.first()
        if repo is not None:
            project.repository_type = repo.type
            project.repository_url = repo.url
            project.save()


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0025_add_repository'),
    ]

    operations = [
        migrations.RunPython(
            copy_repo_attributes_to_relation,
            copy_relation_to_repo_attributes
        ),
    ]
