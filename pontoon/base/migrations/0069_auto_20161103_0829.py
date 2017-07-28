# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-03 08:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0068_auto_20161102_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translation',
            name='approved_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='approved_translations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='translation',
            name='unapproved_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='unapproved_translations', to=settings.AUTH_USER_MODEL),
        ),
    ]
