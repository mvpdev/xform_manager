#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import datetime
from django.db import models
from .. import utils, tag
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.conf import settings
import re

# these cleaners will be used when saving data
# All cleaned types should be in this list
cleaner = {
    u'geopoint': lambda(x): dict(zip(
            ["latitude", "longitude", "altitude", "accuracy"],
            x.split()
            )),
    u'dateTime': lambda(x): datetime.datetime.strptime(
        x.split(".")[0],
        '%Y-%m-%dT%H:%M:%S'
        ),
    }

class XForm(models.Model):
    # web_title is used if the user wants to display a different title
    # on the website
    web_title = models.CharField(max_length=64)
    downloadable = models.BooleanField()
    description = models.TextField(blank=True, null=True, default="")
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'), blank=True,
        help_text=_("Each XForm is assigned to groups, only users in atleast one of this XForm's groups will be able to update this XForm.")
        )
    xml = models.TextField()
    id_string = models.SlugField(
        unique=True, editable=False, verbose_name="ID String"
        )
    title = models.CharField(editable=False, max_length=64)

    class Meta:
        app_label = 'xform_manager'
        verbose_name = "XForm"
        verbose_name_plural = "XForms"
        ordering = ("id_string",)

    def file_name(self):
        return self.id_string + ".xml"

    def url(self):
        return reverse(
            "download_xform",
            kwargs={"id_string" : self.id_string},
            )

    def guarantee_parser(self):
        # there must be a better way than this solution
        if not hasattr(self, "parser"):
            self.parser = utils.XFormParser(self.xml)

    def save(self, *args, **kwargs):
        self.guarantee_parser()
        self.id_string = self.parser.get_id_string()
        if settings.STRICT and not re.search(r"^[\w-]+$", self.id_string):
            raise Exception("In strict mode, the XForm ID must be a valid slug and contain no spaces.")
        self.title = self.parser.get_title()
        super(XForm, self).save(*args, **kwargs)

    def clean_instance(self, data):
        """
                1. variable doesn't start with _
                2. if variable doesn't exist in vardict log message
                3. if there is data and a cleaner, clean that data
        """            
        self.guarantee_parser()
        vardict = self.parser.get_variable_dictionary()
        for path in data.keys():
            if not path.startswith(u"_") and data[path]:
                if path not in vardict:
                    raise utils.MyError(
                        "The XForm %(id_string)s does not describe all "
                        "the variables seen in this instance. "
                        "Specifically, there is no definition for "
                        "%(path)s." % {
                            "id_string" : self.id_string,
                            "path" : path
                            }
                        )
                elif vardict[path][u"type"] in cleaner:
                    data[path] = cleaner[vardict[path][u"type"]](data[path])
        
    def __unicode__(self):
        return getattr(self, "id_string", "")

    def submission_count(self):
        return self.surveys.count()
    submission_count.short_description = "Submission Count"

    def date_of_last_submission(self):
        if self.submission_count() > 0:
            return self.surveys.order_by("-date")[0].date
