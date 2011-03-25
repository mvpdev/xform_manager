#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8

import os, glob
from django.core.management.base import BaseCommand
from django.core.management import call_command

from settings import PROJECT_ROOT
import os

from django.core.serializers import serialize

from xform_manager.models import *
from parsed_xforms.models import *
from surveyor_manager.models import *
from nga_districts import models as nga_models

from django.contrib.auth.models import User

import time
import math

from django.conf import settings

xform_db = settings.MONGO_DB
#xform_instances = xform_db.instances

class Command(BaseCommand):
    help = "Export ODK forms and instances to JSON."

    def handle(self, *args, **kwargs):
        def reset_stuff():
            """
            Resetting mongo_db, Deleting ParsedInstances, Deleting Surveyors.
            """
#            print dir(xform_db)
            try:
                xform_db.instances.drop()
            except Exception, e:
                #i can't believe i'm doing this, but
                # it seems to be the only way to get this to not fail
                # every other time i run it.
                xform_db.instances.drop()
            
            for x in Instance.objects.all():
                pi = ParsedInstance.objects.filter(instance=x)
                if pi.count() > 0:
                    x.parsed_instance.delete()
            for s in Surveyor.objects.all(): s.delete()
            return reset_stuff.__doc__.strip()
        
        def reparsing_instances():
            """
            Calling i.reparse for i in <Instances>
            """
            for i in Instance.objects.all(): i.reparse()
            
        
        look_for_keys = ['instances', 'parsed_instances', 'mongo_instances', \
                'districts_assigned', 'districts_total', 'registrations', 'surveyors', 'users']
        def gather_counts():
            counts = {
                'instances': Instance.objects.count(),
                'parsed_instances': ParsedInstance.objects.count(),
                'districts_assigned': ParsedInstance.objects.exclude(lga=None).count(),
                'districts_total': nga_models.LGA.objects.count(),
                'registrations': Registration.objects.count(),
                'mongo_instances': xform_instances.count(),
                'surveyors': Surveyor.objects.count(),
                'users': User.objects.count()
            }
            return (counts, time.clock())
        
        print "[Reparsing XForm Instances]\n"
        print " --> %s" % reset_stuff.__doc__.strip()
        reset_stuff()
        cts_1, start_time = gather_counts()
        reparsing_instances()
        print " --> %s" % reparsing_instances.__doc__.strip()
        cts_2, end_time = gather_counts()
        print "\nReparsing took [%d ticks] or [??? seconds]." % math.floor(1000*(end_time-start_time))
        
        strs = [[], [], [], []]
        for k in look_for_keys:
            strs[0].append(" %-19s" % k)
            strs[1].append(" %-18d " % cts_1[k])
            strs[2].append(" %-18d " % cts_2[k])
            strs[3].append("--------------------")
        
        print '|'.join(strs[0])
        print '-'.join(strs[3])
        print '|'.join(strs[1])
        print '|'.join(strs[2])
        print "\n"
