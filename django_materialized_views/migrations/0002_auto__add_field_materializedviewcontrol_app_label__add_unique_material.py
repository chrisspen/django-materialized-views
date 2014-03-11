# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'MaterializedViewControl.app_label'
        db.add_column(u'django_materialized_views_materializedviewcontrol', 'app_label',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True),
                      keep_default=False)

        # Adding unique constraint on 'MaterializedViewControl', fields ['name', 'app_label']
        try:
            # MySQL doesn't allow this due to the key length being too long,
            # so it'll just have to do without.
            # e.g. "Specified key was too long; max key length is 767 bytes"
            # If this is a deal breaker, I recommend using a better database
            # like PostgreSQL.
            db.create_unique(u'django_materialized_views_materializedviewcontrol', ['name', 'app_label'])
        except Exception, e:
            pass


    def backwards(self, orm):
        # Removing unique constraint on 'MaterializedViewControl', fields ['name', 'app_label']
        try:
            db.delete_unique(u'django_materialized_views_materializedviewcontrol', ['name', 'app_label'])
        except Exception, e:
            pass

        # Deleting field 'MaterializedViewControl.app_label'
        db.delete_column(u'django_materialized_views_materializedviewcontrol', 'app_label')


    models = {
        u'django_materialized_views.materializedviewcontrol': {
            'Meta': {'unique_together': "(('name', 'app_label'),)", 'object_name': 'MaterializedViewControl'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_in_batch': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'stripable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['django_materialized_views']