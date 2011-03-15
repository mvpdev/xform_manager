from django.db import models
from django.conf import settings

from .xform import XForm
from .survey_type import SurveyType
from .. import utils, tag

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

    class Meta:
        app_label = 'xform_manager'

    def _set_xform(self, doc):
        try:
            self.xform = XForm.objects.get(id_string=doc[tag.XFORM_ID_STRING])
        except XForm.DoesNotExist:
            self.xform = None
            log("The corresponding XForm definition is missing",
                doc[tag.XFORM_ID_STRING])

    def _set_survey_type(self, doc):
        self.survey_type, created = \
            SurveyType.objects.get_or_create(slug=doc[tag.INSTANCE_DOC_NAME])

    def _set_start_time(self, doc):
        self.start_time = doc.get(tag.DATE_TIME_START, None)

    def _set_date(self, doc):
        start_date = doc.get(tag.DATE_TIME_START, None)
        if start_date: self.date = start_date.date()

    def save(self, *args, **kwargs):
        doc = utils.parse_xform_instance(self.xml)
        self._set_xform(doc)
        if self.xform: self.xform.clean_instance(doc)
        self._set_start_time(doc)
        self._set_date(doc)
        self._set_survey_type(doc)
        super(Instance, self).save(*args, **kwargs)

    def get_dict(self):
        """Return a python object representation of this instance's XML."""
        doc = utils.parse_xform_instance(self.xml)
        self.xform.clean_instance(doc)
        return doc
