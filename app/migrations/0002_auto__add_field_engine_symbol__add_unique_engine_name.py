# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Engine.symbol'
        db.add_column(u'app_engine', 'symbol',
                      self.gf('django.db.models.fields.CharField')(max_length=10, unique=True, null=True),
                      keep_default=False)

        # Adding unique constraint on 'Engine', fields ['name']
        db.create_unique(u'app_engine', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Engine', fields ['name']
        db.delete_unique(u'app_engine', ['name'])

        # Deleting field 'Engine.symbol'
        db.delete_column(u'app_engine', 'symbol')


    models = {
        u'app.engine': {
            'Meta': {'ordering': "['name']", 'object_name': 'Engine'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True'})
        }
    }

    complete_apps = ['app']