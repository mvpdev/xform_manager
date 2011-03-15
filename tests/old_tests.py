"""
Testing POSTs to "/submission"
"""
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings
import os
from xform_manager.models import XForm, Instance
from xform_manager import urls
from xform_manager import utils
import datetime

from xform_manager.factory import XFormManagerFactory, _load_registration_survey_object

class TextXFormCreation(TestCase):

    def test_xform_creation(self):
        f = open(os.path.join(
                settings.PROJECT_ROOT, "xform_manager",
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

class TextFactoryXFormCreation(TestCase):
    def setUp(self):
        self.xform_factory = XFormManagerFactory()

    def test_factory_creation_of_registration_xform(self):
        xf = self.xform_factory.create_registration_xform()
        registration_form_count = XForm.objects.filter(title="registration").count()
        self.assertEqual(1, registration_form_count)
    
    def test_factory_creation_of_simple_xform(self):
        xf = self.xform_factory.create_simple_xform()
        all_form_count = XForm.objects.count()
        self.assertEqual(1, all_form_count)
    
    def test_factory_creation_of_registration_instance(self):
        self.assertEqual(0, Instance.objects.count())
        xi = self.xform_factory.create_registration_instance()
        self.assertEqual(1, Instance.objects.count())
    
    def test_factory_creation_of_simple_instance(self):
        self.assertEqual(0, Instance.objects.count())
        xi = self.xform_factory.create_simple_instance()
        self.assertEqual(1, Instance.objects.count())

class TestFormSubmission(TestCase):
    def setUp(self):
        self.xform_factory = XFormManagerFactory()
        self.registration_form = self.xform_factory.create_registration_xform()
    
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
        pz = _load_registration_survey_object().instantiate()
        pz.answer('start', '2011-01-01T09:50:06.966')
        pz.answer('end', '2011-01-01T09:53:22.965')
        pz.answer('device_id', '98765')
        pz.answer('name', 'Stewie')
        
        tfile_path = "registration.xml"
        tfile_w = open(tfile_path, 'w')
        tfile_w.write(pz.to_xml())
        tfile_w.close()
        
        tfile = open(tfile_path, 'r')
        post_data = {
            "xml_submission_file" : tfile,
        }
        # I wish django testcase made it easier to test file uploads....!
        response = self.client.post("/submission", post_data)
        tfile.close()
        
        self.assertEqual(response.status_code, 201)

    def test_parse_xform_instance(self):
        xml_str = """<?xml version='1.0' ?><test id="test_id"><a>1</a><b>2</b></test>"""
        expected_obj = (u"test", [
                (u"a", u"1"),
                (u"b", u"2"),
                ])
        pyobj = utils._xmlstr2pyobj(xml_str)
        self.assertEqual(pyobj, expected_obj)
        expected_dict = {
            (u"test",) : 1,
            (u"test", u"a") : 1,
            (u"test", u"b") : 1,
            }
        self.assertEqual(utils._count_xpaths(pyobj), expected_dict)
        self.assertEqual(utils.parse_xform_instance(xml_str), {
                u'_name': u'test',
                u'_id_string': u'test_id',
                u'a': u'1',
                u'b': u'2',
                })

        xml_str = """<?xml version='1.0' ?><test id="test_id"><a><b>2</b></a></test>"""
        expected_obj = (u"test", [
                (u"a", [(u"b", u"2")])
                ])
        pyobj = utils._xmlstr2pyobj(xml_str)
        self.assertEqual(pyobj, expected_obj)
        expected_dict = {
            (u"test",) : 1,
            (u"test", u"a") : 1,
            (u"test", u"a", u"b") : 1,
            }
        self.assertEqual(utils._count_xpaths(pyobj), expected_dict)
        self.assertEqual(utils.parse_xform_instance(xml_str), {
                u'_id_string': u'test_id',
                u'a/b': u'2',
                u'_name': u'test',
                })

        xml_str = """<?xml version='1.0' ?><test id="test_id"><b>1</b><b>2</b></test>"""
        expected_obj = (u'test', [
                (u"b", u"1"),
                (u"b", u"2"),
                ])
        pyobj = utils._xmlstr2pyobj(xml_str)
        self.assertEqual(pyobj, expected_obj)
        expected_dict = {
            (u"test",) : 1,
            (u"test", u"b") : 2,
            }
        self.assertEqual(utils._count_xpaths(pyobj), expected_dict)
        self.assertEqual(utils.parse_xform_instance(xml_str), {
                u'_name': u'test',
                u'_id_string': u'test_id',
                u'b[0]': u'1',
                u'b[1]': u'2',
                })
