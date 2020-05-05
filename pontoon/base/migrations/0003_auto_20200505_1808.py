# Generated by Django 2.2.11 on 2020-05-05 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20200322_1821'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('pk',), 'permissions': (('can_manage_project', 'Can manage project'),)},
        ),
        migrations.AddField(
            model_name='project',
            name='visibility',
            field=models.CharField(choices=[('private', 'Private'), ('public', 'Public')], default='private', max_length=20),
        ),
    ]
