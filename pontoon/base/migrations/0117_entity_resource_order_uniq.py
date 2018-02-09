# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-09 14:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0116_fix_ambiguous_entity_order'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together=set([('resource', 'order')]),
        ),
    ]
