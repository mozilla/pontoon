# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0034_remove_deleted_translations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='translation',
            name='deleted',
        ),
        migrations.AlterField(
            model_name='repository',
            name='source_repo',
            field=models.BooleanField(default=False, help_text=b'\n        If true, this repo contains the source strings directly in the\n        root of the repo. Checkouts of this repo will have "templates"\n        appended to the end of their path so that they are detected as\n        source directories.\n    '),
        ),
    ]
