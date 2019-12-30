# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0045_remove_can_localize"),
    ]

    operations = [
        migrations.RemoveField(model_name="userprofile", name="svn_password",),
        migrations.RemoveField(model_name="userprofile", name="svn_username",),
        migrations.RemoveField(model_name="userprofile", name="transifex_password",),
        migrations.RemoveField(model_name="userprofile", name="transifex_username",),
        migrations.AddField(
            model_name="userprofile",
            name="force_suggestions",
            field=models.BooleanField(default=False),
        ),
    ]
