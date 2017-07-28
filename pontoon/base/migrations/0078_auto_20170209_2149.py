# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 21:49
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import pontoon.base.models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0077_repository_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locale',
            name='cldr_plurals',
            field=models.CharField(blank=True, help_text=b'\n        A comma separated list of <a href="http://www.unicode.org/cldr/charts/dev/supplemental/language_plural_rules.html">CLDR plural rules</a>,\n        where 0 represents zero, 1 one, 2 two, 3 few, 4 many, and 5 other.\n        E.g. 1,5\n        ',
                                   max_length=11, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.'), pontoon.base.models.validate_cldr], verbose_name=b'CLDR Plurals'),
        ),
    ]
