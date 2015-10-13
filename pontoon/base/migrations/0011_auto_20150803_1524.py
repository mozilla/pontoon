# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_translation_extra'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locale',
            options={'ordering': ['name']},
        ),
    ]
