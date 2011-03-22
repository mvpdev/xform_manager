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
        self.start_time = None # doc.get(tag.DATE_TIME_START, None)

    def _set_date(self, doc):
        self.date = None
        # start_date = doc.get(tag.DATE_TIME_START, None)
        # if start_date: self.date = start_date.date()

    def reparse(self):
        if self.parsed_instance:
            self.parsed_instance.delete()
        self.save()

    def save(self, *args, **kwargs):
        doc = utils.parse_xform_instance(self.xml)
        self._set_xform(doc)
        self._set_start_time(doc)
        self._set_date(doc)
        self._set_survey_type(doc)
        super(Instance, self).save(*args, **kwargs)

    def get_dict(self):
        """Return a python object representation of this instance's XML."""
        return utils.parse_xform_instance(self.xml)

    def get_list_of_pairs(self):
        return utils._xmlstr2pyobj(self.xml)

    def as_html(self):
        def pair2html(pair, level):
            if type(pair[1])==list:
                # note we should deal with levels of headers here
                result = "<h%(level)s>%(key)s</h%(level)s>" % \
                    {"level" : level, "key" : pair[0]}
                for value in pair[1]:
                    result += pair2html(value, level+1)
                return result
            else:
                return "%(key)s : %(value)s<br/>" % \
                    {"key" : pair[0], "value" : pair[1]}
        return pair2html(self.get_list_of_pairs(), 1)
