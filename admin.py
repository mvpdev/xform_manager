from django.contrib import admin
from trkr.xform_manager.models.instance import Instance
from trkr.xform_manager.models.attachment import Attachment
from trkr.xform_manager.models.survey_type import SurveyType
from trkr.xform_manager.models.xform import XForm

admin.site.register(Instance)
admin.site.register(Attachment)
admin.site.register(SurveyType)
admin.site.register(XForm)