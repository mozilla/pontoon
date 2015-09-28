# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_changedentitylocale_when'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repository',
            name='multi_locale',
        ),
    ]
