#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from . import views

# Here are some url names that we'll need to reference multiple times.
DOWNLOAD_XFORM = "download-xform"
LIST_XFORMS = "list_xforms"
FORM_LIST = "form-list"

#ODK Collect URLS:
#-general:
#    /formList
#    /submission
#-group-specific:
#    /group_name/formList
#    /group_name/submission

#browser accessible urls
#-general:
#    /
#    /x/new
#    /x/show
#    /x/hide
#    /x/(xform_id) #edit
#    /x/(xform_id).xml #download
#-group-specific:
#    /group_name/
#    /group_name/x/new
#    /group_name/x/show
#    /group_name/x/hide
#    /group_name/x/(xform_id)
#    /group_name/x/(xform_id).xml

#For debugging with no groups: OPT_GROUP_REGEX = ""
OPT_GROUP_REGEX = "((?P<group_name>[^/]+)/)?"

urlpatterns = patterns('',
    url(r"^%sformList$" % OPT_GROUP_REGEX, views.formList, name=FORM_LIST),
    url(r"^%ssubmission$" % OPT_GROUP_REGEX, views.submission),

    url(r"^%sx/new/$" % OPT_GROUP_REGEX, views.create_xform),
    url(r"^%sx/(?P<id>\S+)\.xml$" % OPT_GROUP_REGEX, views.download_xform, name=DOWNLOAD_XFORM),
    url(r"^%sx/(?P<pk>\S+)/(?P<show_hide>(show|hide))$" % OPT_GROUP_REGEX, views.show_hide_xform),
    url(r"^%sx/(?P<id>\S+)/$" % OPT_GROUP_REGEX, views.show_xform),
    url(r"^%s$" % OPT_GROUP_REGEX, views.list_xforms, name=LIST_XFORMS),
)
