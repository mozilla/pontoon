# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-05-27 23:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0062_auto_20160520_0040"),
    ]

    operations = [
        migrations.RemoveField(model_name="project", name="has_changed",),
    ]
