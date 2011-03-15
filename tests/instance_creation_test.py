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

    def test_instance_creation(self):
        xml_file = open(os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "Health_2011_03_13.xml_2011-03-15_20-30-28",
                "Health_2011_03_13.xml_2011-03-15_20-30-28.xml"
                ))
        # note the "rb" mode is to open a binary file
        image_file = open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "Health_2011_03_13.xml_2011-03-15_20-30-28",
                "1300221157303.jpg"),
            "rb")

        # ODK Collect uses the name of the jpg file as the key in the
        # post.
        postdata = {"xml_submission_file" : xml_file,
                    "1300221157303.jpg" : image_file}
        response = self.client.post('/submission', postdata)
        self.failUnlessEqual(response.status_code, 201)
