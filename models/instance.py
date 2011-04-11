from django.db import models
from django.conf import settings

from .xform import XForm
from .survey_type import SurveyType
from xform_manager.xform_instance_parser import XFormInstanceParser

from common_tags import XFORM_ID_STRING

from datetime import datetime

def log(*args, **kwargs):
    """
    This is a place holder for a real logging function.
    """
    pass

class Instance(models.Model):
    # I should rename this model, maybe Survey
    xml = models.TextField()

    #using instances instead of surveys breaks django
    xform = models.ForeignKey(XForm, null=True, related_name="surveys")
    start_time = models.DateTimeField(null=True)
    date = models.DateField(null=True)
    survey_type = models.ForeignKey(SurveyType)
    
    #shows when we first received this instance
    date_created = models.DateTimeField(auto_now_add=True)
    #this will end up representing "date last parsed"
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'xform_manager'

    def _set_xform(self, doc):
        try:
            self.xform = XForm.objects.get(id_string=doc[XFORM_ID_STRING])
        except XForm.DoesNotExist:
            self.xform = None
            log("The corresponding XForm definition is missing",
                doc[XFORM_ID_STRING])

    def get_root_node_name(self):
        self._set_parser()
        return self._parser.get_root_node_name()

    def get(self, abbreviated_xpath):
        self._set_parser()
        return self._parser.get(abbreviated_xpath)

    def _set_survey_type(self, doc):
        self.survey_type, created = \
            SurveyType.objects.get_or_create(slug=self.get_root_node_name())

    # todo: get rid of these fields
    def _set_start_time(self, doc):
        self.start_time = None

    def _set_date(self, doc):
        self.date = None

    def save(self, *args, **kwargs):
        doc = self.get_dict()
        self._set_xform(doc)
        self._set_start_time(doc)
        self._set_date(doc)
        self._set_survey_type(doc)
        super(Instance, self).save(*args, **kwargs)

    def _set_parser(self):
        if not hasattr(self, "_parser"):
            self._parser = XFormInstanceParser(self.xml)

    def get_dict(self, force_new=False):
        """Return a python object representation of this instance's XML."""
        self._set_parser()
        return self._parser.get_flat_dict_with_attributes()
