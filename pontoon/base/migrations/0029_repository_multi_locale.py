# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_auto_20150915_0013'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='multi_locale',
            field=models.BooleanField(default=False, help_text=b'\n        If true, this repo corresponds to multiple locale-specific repos. The\n        URL should have the string "{locale_code}" in it, which will be replaced\n        by the locale codes of all enabled locales for the project during pulls\n        and and commits.\n    '),
        ),
    ]
