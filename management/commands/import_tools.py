#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8

import os, glob
from django.core.management.base import BaseCommand
from django.core.management import call_command

from xform_manager.import_tools import import_instances_from_jonathan

from xform_manager.models import Instance, XForm
from parsed_xforms.models import ParsedInstance, Registration
from nga_districts import models as nga_models
from surveyor_manager.models import Surveyor

from django.contrib.auth.models import User
from django.conf import settings

xform_db = settings.MONGO_DB
xform_instances = xform_db.instances

import time, math


def get_counts():
    cols = ['instances', 'parsed_instances', 'mongo_instances', \
            'registrations', 'surveyors', 'users', 'images']
    counts = {
        'instances': Instance.objects.count(),
        'parsed_instances': ParsedInstance.objects.count(),
        'districts_assigned': ParsedInstance.objects.exclude(lga=None).count(),
        'districts_total': nga_models.LGA.objects.count(),
        'registrations': Registration.objects.count(),
        'mongo_instances': xform_instances.count(),
        'images': len(glob.glob(os.path.join(IMAGES_DIR, '*'))),
        'surveyors': Surveyor.objects.count(),
        'users': User.objects.count()
    }
    return (cols, counts, time.clock())

def display_counts_as_table(cols, list_of_dicts):
    strs = [[] for row in list_of_dicts]
    col_heads = []
    breaker = []
    for c in cols:
        col_heads.append(" %-19s" % c)
        breaker.append("--------------------")
        for i in range(0, len(list_of_dicts)):
            strs[i].append(" %-18d " % list_of_dicts[i][c])
    
    print '|'.join(col_heads)
    print '-'.join(breaker)
    for starr in strs:
        print '|'.join(starr)

IMAGES_DIR = os.path.join(settings.MEDIA_ROOT, "attachments")

class Command(BaseCommand):
    help = "Import ODK forms and instances."

    def handle(self, *args, **kwargs):
        path = args[0]
        print "[Importing XForm Instances from %s]\n" % path
        cols, counts_1, start_time = get_counts()
#        import_instances_from_jonathan(path)
        cols, counts_2, end_time = get_counts()
        display_counts_as_table(cols, [counts_1, counts_2])
        
#        print glob.glob(os.path.join(path, "*"))
#        call_command('import_forms', os.path.join(path, "forms"))
#        call_command('import_instances', os.path.join(path, "instances"))
