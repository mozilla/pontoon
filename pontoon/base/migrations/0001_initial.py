# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.TextField()),
                ('string_plural', models.TextField(blank=True)),
                ('key', models.TextField(blank=True)),
                ('comment', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('source', models.TextField(blank=True)),
                ('obsolete', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Locale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=128)),
                ('nplurals', models.SmallIntegerField(null=True, blank=True)),
                ('plural_rule', models.CharField(max_length=128, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('slug', models.SlugField(unique=True)),
                ('repository_type', models.CharField(default=b'File', max_length=20, verbose_name=b'Type', choices=[(b'file', b'File'), (b'git', b'Git'), (b'hg', b'HG'), (b'svn', b'SVN'), (b'transifex', b'Transifex')])),
                ('repository_url', models.CharField(max_length=2000, verbose_name=b'URL', blank=True)),
                ('repository_path', models.TextField(blank=True)),
                ('transifex_project', models.CharField(max_length=128, verbose_name=b'Project', blank=True)),
                ('transifex_resource', models.CharField(max_length=128, verbose_name=b'Resource', blank=True)),
                ('info_brief', models.TextField(verbose_name=b'Project info', blank=True)),
                ('url', models.URLField(verbose_name=b'URL', blank=True)),
                ('width', models.PositiveIntegerField(null=True, verbose_name=b'Default website (iframe) width in pixels. If set,         sidebar will be opened by default.', blank=True)),
                ('links', models.BooleanField(verbose_name=b'Keep links on the project website clickable')),
                ('disabled', models.BooleanField(default=False)),
                ('locales', models.ManyToManyField(to='base.Locale')),
            ],
            options={
                'permissions': (('can_manage', 'Can manage projects'), ('can_localize', 'Can localize projects')),
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.TextField()),
                ('entity_count', models.PositiveIntegerField(default=0)),
                ('format', models.CharField(blank=True, max_length=20, verbose_name=b'Format', choices=[(b'po', b'po'), (b'properties', b'properties'), (b'dtd', b'dtd'), (b'ini', b'ini'), (b'lang', b'lang')])),
                ('project', models.ForeignKey(to='base.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translated_count', models.PositiveIntegerField(default=0)),
                ('approved_count', models.PositiveIntegerField(default=0)),
                ('fuzzy_count', models.PositiveIntegerField(default=0)),
                ('locale', models.ForeignKey(to='base.Locale')),
                ('resource', models.ForeignKey(to='base.Resource')),
            ],
        ),
        migrations.CreateModel(
            name='Subpage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('url', models.URLField(verbose_name=b'URL', blank=True)),
                ('project', models.ForeignKey(to='base.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.TextField()),
                ('plural_form', models.SmallIntegerField(null=True, blank=True)),
                ('date', models.DateTimeField()),
                ('approved', models.BooleanField(default=False)),
                ('approved_date', models.DateTimeField(null=True, blank=True)),
                ('fuzzy', models.BooleanField(default=False)),
                ('approved_user', models.ForeignKey(related_name='approvers', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(to='base.Entity')),
                ('locale', models.ForeignKey(to='base.Locale')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transifex_username', models.CharField(max_length=40, blank=True)),
                ('transifex_password', models.CharField(max_length=128, blank=True)),
                ('svn_username', models.CharField(max_length=40, blank=True)),
                ('svn_password', models.CharField(max_length=128, blank=True)),
                ('quality_checks', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='entity',
            name='resource',
            field=models.ForeignKey(to='base.Resource'),
        ),
    ]
