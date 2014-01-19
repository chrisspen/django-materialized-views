# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MaterializedViewControl'
        db.create_table(u'django_materialized_views_materializedviewcontrol', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('stripable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('include_in_batch', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'django_materialized_views', ['MaterializedViewControl'])


    def backwards(self, orm):
        # Deleting model 'MaterializedViewControl'
        db.delete_table(u'django_materialized_views_materializedviewcontrol')


    models = {
        u'django_materialized_views.materializedviewcontrol': {
            'Meta': {'object_name': 'MaterializedViewControl'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_in_batch': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'stripable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['django_materialized_views']