from django.test import TestCase, Client
from xform_manager.models import XForm, Instance
import os

class TestWaterSubmission(TestCase):

    def test_xform_creation(self):
        f = open(os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "Water_Translated_2011_03_10.xml"
                ))
        xml = f.read()
        f.close()
        xform = XForm.objects.create(
            xml=xml
            )

    def test_form_submission(self):
        f = open(os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "Water_Translated_2011_03_10_2011-03-10_14-38-28.xml"
                ))
        xml = f.read()
        f.close()
        instance = Instance.objects.create(
            xml=xml
            )
        
