"""
Testing POSTs to "/submission"
"""
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
import os
from .models import XForm
from . import urls

class TextXFormCreation(TestCase):
    def test_xform_creation(self):
        f = open(os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "fixtures", "test_forms", "registration", "forms",
                "test_registration.xml"
                ))
        xml = f.read()
        f.close()
        xform = XForm.objects.create(
            web_title="blah",
            xml=xml
            )
        self.assertEqual(xform.xml, xml)
        self.assertEqual(xform.id_string, "Registration2010-12-04_09-34-00")
        self.assertEqual(xform.title, "Registration")
        self.assertEqual(xform.file_name(), "Registration2010-12-04_09-34-00.xml")
        self.assertTrue(xform.url().endswith("Registration2010-12-04_09-34-00.xml"))

class TestFormSubmission(TestCase):
    def tests_formlist(self):
        response = self.client.get(reverse(urls.FORM_LIST))
        self.assertEqual(response.status_code, 200)
    
    def test_empty_post(self):
        """
        The status code is not 200 if the user submits a bad/empty survey
        """
        response = self.client.post("/submission", {})
        self.assertNotEqual(response.status_code, 200)
    
    def test_form_post(self):
        """
        xml_submission_file is the field name for the posted xml file.
        """
        post_data = {
            "xml_submission_file" : (
                "filename.xml",
                #this xml text is not the right way to post a file, so should be replaced.
                "<?xml version='1.0' ?><Example id='Simple Photo Survey'><Location><Picture>1286990143958.jpg</Picture></Location></Example>",
            )
        }
        response = self.client.post("/submission", post_data)
        # self.assertEqual(response.status_code, 200)


