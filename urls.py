#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from . import views

# Here are some url names that we'll need to reference multiple times.
DOWNLOAD_XFORM = "download-xform"
LIST_XFORMS = "list-xforms"
FORM_LIST = "form-list"

urlpatterns = patterns('',
    url(r"^formList$", views.formList, name=FORM_LIST),
    url(r"^download-xform/(?P<id_string>[^/]+)\.xml$",
        views.download_xform, name=DOWNLOAD_XFORM),
    url(r"^submission$", views.submission),

    url(r"^create-xform/$", views.create_xform),
    url(r"^list-xforms/$", views.list_xforms, name=LIST_XFORMS),
    url(r"^update-xform/(?P<pk>\d+)/$", views.update_xform),
)
