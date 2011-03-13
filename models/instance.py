from django.db import models
from django.dispatch import Signal

from django.conf import settings

from .xform import XForm
from .survey_type import SurveyType
from .. import utils, tag


#i'm not sure where this _should_ go so I'll put it here for now.
# this is a signal that is called at some point after the instance created
# it triggers the "_set_xform", "_set_phone", etc. chain.
INSTANCE_PROCESS_SIGNAL = Signal(providing_args=["instance", "raw"])

class Instance(models.Model):
    # I should rename this model, maybe Survey
    xml = models.TextField()

    #using instances instead of surveys breaks django
    xform = models.ForeignKey(XForm, related_name="surveys", null=True)
    start_time = models.DateTimeField(null=True)
    date = models.DateField(null=True)
    survey_type = models.ForeignKey(SurveyType, null=True)

    class Meta:
        app_label = 'xform_manager'

    def _set_xform(self, doc):
        try:
            self.xform = XForm.objects.get(id_string=doc[tag.XFORM_ID_STRING])
        except XForm.DoesNotExist:
            raise utils.MyError(
                "Missing corresponding XForm: %s" % \
                doc[tag.XFORM_ID_STRING]
                )

    def _set_survey_type(self, doc):
        self.survey_type, created = \
            SurveyType.objects.get_or_create(slug=doc[tag.INSTANCE_DOC_NAME])

    def _set_start_time(self, doc):
        self.start_time = doc[tag.DATE_TIME_START]

    def _set_date(self, doc):
        self.date = doc[tag.DATE_TIME_START].date()

    def process(self, *args, **kwargs):
        doc = utils.parse_xform_instance(self.xml)
        self._set_xform(doc)
        self.xform.clean_instance(doc)
        self._set_start_time(doc)
        self._set_date(doc)
        self._set_survey_type(doc)
#        super(Instance, self).save(*args, **kwargs)
        INSTANCE_PROCESS_SIGNAL.send(sender=self.__class__, instance=self)

    def get_dict(self):
        """Return a python object representation of this instance's XML."""
        doc = utils.parse_xform_instance(self.xml)
        self.xform.clean_instance(doc)
        return doc
