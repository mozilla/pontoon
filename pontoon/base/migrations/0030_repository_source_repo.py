# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_repository_multi_locale'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='source_repo',
            field=models.BooleanField(default=False, help_text=b'\n        If true, this repo contains the source strings directly in the\n        root of the repo. Checkouts of this repo will have "en-US"\n        appended to the end of their path so that they are detected as\n        source directories.\n    '),
        ),
    ]
