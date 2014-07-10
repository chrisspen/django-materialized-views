# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'MaterializedViewControl.name'
        db.alter_column(u'django_materialized_views_materializedviewcontrol', 'name', self.gf('django.db.models.fields.CharField')(max_length=250))

        # Changing field 'MaterializedViewControl.app_label'
        db.alter_column(u'django_materialized_views_materializedviewcontrol', 'app_label', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

    def backwards(self, orm):

        # Changing field 'MaterializedViewControl.name'
        db.alter_column(u'django_materialized_views_materializedviewcontrol', 'name', self.gf('django.db.models.fields.CharField')(max_length=500))

        # Changing field 'MaterializedViewControl.app_label'
        db.alter_column(u'django_materialized_views_materializedviewcontrol', 'app_label', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

    models = {
        'django_materialized_views.materializedviewcontrol': {
            'Meta': {'unique_together': "(('name', 'app_label'),)", 'object_name': 'MaterializedViewControl'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_in_batch': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'stripable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['django_materialized_views']