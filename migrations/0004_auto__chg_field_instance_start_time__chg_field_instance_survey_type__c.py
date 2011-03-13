# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Instance.start_time'
        db.alter_column('xform_manager_instance', 'start_time', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Instance.survey_type'
        db.alter_column('xform_manager_instance', 'survey_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xform_manager.SurveyType'], null=True))

        # Changing field 'Instance.date'
        db.alter_column('xform_manager_instance', 'date', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Instance.xform'
        db.alter_column('xform_manager_instance', 'xform_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['xform_manager.XForm']))

        # Deleting field 'SurveyType.map_icon_color'
        db.delete_column('xform_manager_surveytype', 'map_icon_color')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Instance.start_time'
        raise RuntimeError("Cannot reverse this migration. 'Instance.start_time' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Instance.survey_type'
        raise RuntimeError("Cannot reverse this migration. 'Instance.survey_type' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Instance.date'
        raise RuntimeError("Cannot reverse this migration. 'Instance.date' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Instance.xform'
        raise RuntimeError("Cannot reverse this migration. 'Instance.xform' and its values cannot be restored.")

        # Adding field 'SurveyType.map_icon_color'
        db.add_column('xform_manager_surveytype', 'map_icon_color', self.gf('django.db.models.fields.CharField')(default='Black', max_length=12), keep_default=False)


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'xform_manager.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['xform_manager.Instance']"}),
            'media_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'xform_manager.instance': {
            'Meta': {'object_name': 'Instance'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'survey_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['xform_manager.SurveyType']", 'null': 'True'}),
            'xform': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'surveys'", 'null': 'True', 'to': "orm['xform_manager.XForm']"}),
            'xml': ('django.db.models.fields.TextField', [], {})
        },
        'xform_manager.surveytype': {
            'Meta': {'object_name': 'SurveyType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'xform_manager.xform': {
            'Meta': {'ordering': "('id_string',)", 'object_name': 'XForm'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'downloadable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_string': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'web_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'xml': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['xform_manager']
