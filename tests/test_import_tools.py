from django.test import TestCase, Client
from xform_manager.models import XForm, Instance
import os, glob

from django.core.management import call_command

CUR_PATH = os.path.abspath(__file__)
DB_FIXTURES_PATH = os.path.join(CUR_PATH, 'data_from_sdcard')

from django.conf import settings

def images_count():
    return len(glob.glob(os.path.join(settings.MEDIA_ROOT, 'attachments', '*')))

class TestImportingDatabase(TestCase):
    def test_something(self):
        i = Instance.objects.count()
        ims = images_count()
        call_command('import_tools', DB_FIXTURES_PATH)
        
        i2 = Instance.objects.count()
        ims2 = images_count()
#        self.assertEqual(ims + 1, ims2)


"""
b1:
1 photo survey (completed)
1 simple survey (not marked complete)

b2:
1 photo survey (duplicate, completed)
1 simple survey (marked as complete)
"""