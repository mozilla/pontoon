# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('base_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('transifex_username', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('transifex_password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('svn_username', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('svn_password', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('base', ['UserProfile'])

        # Adding model 'Locale'
        db.create_table('base_locale', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('base', ['Locale'])

        # Adding model 'Project'
        db.create_table('base_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('repository_type', self.gf('django.db.models.fields.CharField')(default='File', max_length=20)),
            ('repository', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('repository_path', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('transifex_project', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('transifex_resource', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('info_brief', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('info_locales', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('info_audience', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('info_metrics', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('external', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('links', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('base', ['Project'])

        # Adding M2M table for field locales on 'Project'
        m2m_table_name = db.shorten_name('base_project_locales')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['base.project'], null=False)),
            ('locale', models.ForeignKey(orm['base.locale'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'locale_id'])

        # Adding model 'Subpage'
        db.create_table('base_subpage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('base', ['Subpage'])

        # Adding model 'Entity'
        db.create_table('base_entity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Project'])),
            ('string', self.gf('django.db.models.fields.TextField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('key', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Entity'])

        # Adding model 'Translation'
        db.create_table('base_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Entity'])),
            ('locale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Locale'])),
            ('string', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('base', ['Translation'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table('base_userprofile')

        # Deleting model 'Locale'
        db.delete_table('base_locale')

        # Deleting model 'Project'
        db.delete_table('base_project')

        # Removing M2M table for field locales on 'Project'
        db.delete_table(db.shorten_name('base_project_locales'))

        # Deleting model 'Subpage'
        db.delete_table('base_subpage')

        # Deleting model 'Entity'
        db.delete_table('base_entity')

        # Deleting model 'Translation'
        db.delete_table('base_translation')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'base.entity': {
            'Meta': {'object_name': 'Entity'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Project']"}),
            'source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'string': ('django.db.models.fields.TextField', [], {})
        },
        'base.locale': {
            'Meta': {'object_name': 'Locale'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'base.project': {
            'Meta': {'object_name': 'Project'},
            'external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_audience': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'info_brief': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'info_locales': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'info_metrics': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'links': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'locales': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.Locale']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'repository': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'repository_path': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'repository_type': ('django.db.models.fields.CharField', [], {'default': "'File'", 'max_length': '20'}),
            'transifex_project': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'transifex_resource': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'base.subpage': {
            'Meta': {'object_name': 'Subpage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Project']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'base.translation': {
            'Meta': {'object_name': 'Translation'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Locale']"}),
            'string': ('django.db.models.fields.TextField', [], {})
        },
        'base.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'svn_password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'svn_username': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'transifex_password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'transifex_username': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['base']