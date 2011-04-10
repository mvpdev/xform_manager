# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from xform_manager.xform_instance_parser import xform_instance_to_dict, \
    xform_instance_to_flat_dict, parse_xform_instance

XML = u"xml"
DICT = u"dict"
FLAT_DICT = u"flat_dict"
ID = u"id"

class TestXFormInstanceParser(TestCase):

    def setUp(self):
        self.inputs_and_outputs = [
            {
                XML: u"""<?xml version='1.0' ?><test id="test_id"><a>1</a><b>2</b></test>""",
                DICT: {
                    u"test": {
                        u"a": u"1",
                        u"b": u"2",
                        }
                    },
                FLAT_DICT: {
                    u"a": u"1",
                    u"b": u"2",
                    },
                ID : u"test_id",
                },
            {
                XML: u"""<?xml version='1.0' ?><test id="test_id"><a><b>2</b></a></test>""",
                DICT: {
                    u"test": {
                        u"a" : {
                            u"b" : u"2"
                            }
                        }
                    },
                FLAT_DICT: {
                    u"a/b" : u"2"
                    },
                ID: u"test_id"
                },
            {
                XML: u"""<?xml version='1.0' ?><test id="test_id"><b>1</b><b>2</b></test>""",
                DICT: {
                    u"test" : {
                        u"b" : [u"1", u"2"]
                        }
                    },
                FLAT_DICT: {
                    u"b[0]": u"1",
                    u"b[1]": u"2"
                    },
                ID: u"test_id"
                },
            {
                XML: u"""
<?xml version='1.0' ?>
<test id="test_id">
  <a>
    <b>1</b>
  </a>
  <a>
    <b>2</b>
  </a>
</test>
""",
                DICT: {
                    u"test" : {
                        u"a" : [{u"b" : u"1"}, {u"b": u"2"}]
                        }
                    },
                FLAT_DICT: {
                    u"a[0]/b": u"1",
                    u"a[1]/b": u"2"
                    },
                ID: u"test_id"
                },

            ]            

    def test_parse_xform_instance(self):
        # todo: need to test id string as well
        for d in self.inputs_and_outputs:
            self.assertEqual(xform_instance_to_dict(d[XML]), d[DICT])
            self.assertEqual(xform_instance_to_flat_dict(d[XML]), d[FLAT_DICT])
            flat_dict_with_id = {u"id": d[ID]}
            flat_dict_with_id.update(d[FLAT_DICT])
            self.assertEqual(parse_xform_instance(d[XML]), flat_dict_with_id)