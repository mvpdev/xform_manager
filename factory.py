# This factory is not the same as the others, and doesn't use
# django-factories but it mimics their functionality...

from xform_manager.models import XForm, Instance
import os
from datetime import datetime

class XFormManagerFactory(object):

    def get_registration_xform(self):
        """
        Gets a registration xform. (currently loaded in from fixture)
        Returns it without saving.
        """
        return load_xform_from_xml_file("xform_manager/fixtures/test_forms/registration/forms/test_registration.xml")
        
    def create_registration_xform(self):
        """
        Calls 'get_registration_xform', saves the result, and returns.
        """
        xf = self.get_registration_xform()
        xf.save()
        return xf

    def get_registration_instance(self, custom_values={}):
        """
        1. Checks to see if the registration form has been created alread. If not, it loads it in.
        
        2. Loads a registration instance.
        """
        registration_xforms = XForm.objects.filter(title="Registration")
        if registration_xforms.count() == 0:
            xf = self.create_registration_xform()
        else:
            xf = registration_xforms[0]
        
        custom_values.update({'form_id': xf.id_string})
        return load_registration_with_values(custom_values)
    
    def create_registration_instance(self, custom_values={}):
        i = self.get_registration_instance(custom_values)
        i.save()
        return i
    
    def get_simple_xform(self):
        """
        Loads a simple XForm and returns. (Currently using the watersimple fixture)
        """
        return load_xform_from_xml_file("xform_manager/fixtures/test_forms/water_simple/forms/WaterSimple.xml")
    
    def create_simple_xform(self):
        xf = self.get_simple_xform()
        xf.save()
        return xf
    
    def get_simple_instance(self, custom_values={}):
        simple_xforms = XForm.objects.filter(title="build_WaterSimple_1295821382")
        if simple_xforms.count() == 0:
            xf = self.create_simple_xform()
        else:
            xf = simple_xforms[0]
    
        custom_values.update({'form_id': xf.id_string})
        return load_simple_submission(custom_values)
    
    def create_simple_instance(self, custom_values={}):
        i = self.get_simple_instance(custom_values)
        i.save()
        return i
        

XFORM_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000"

def load_xform_from_xml_file(filename):
    xf = XForm()
    xf.xml = open(filename).read()
    return xf

def load_registration_with_values(custom_values):
    """
    A hacky way to load values into an XForm, but it *works*. Let's replace this
    when we can find a way to do this better.
    
    values are set to default and overridden by custom_values.
    """
    values = {'device_id': '12345',
        'form_id': 'Registration 2010-12-04_09-34-00',
        'start_time': '2011-01-01T09:50:06.966',
        'end_time': '2011-01-01T09:53:22.965',
        'name': 'Alexander',
        'sex': 'male',
        'birth_date': '1986-08-15',
        'languages': 'English'
    }
    if 'start_time' in custom_values:
        st = custom_values['start_time']
        custom_values['start_time'] = st.strftime(XFORM_TIME_FORMAT)
        
        #if no end_time is specified, defaults to 1 hour
        values['end_time'] = datetime(st.year, st.month, st.day, st.hour+1).strftime(XFORM_TIME_FORMAT)
    
    if 'end_time' in custom_values:
        custom_values['end_time'] = custom_values['end_time'].strftime(XFORM_TIME_FORMAT)
    
    values.update(custom_values)
    registration_xml_template = open('xform_manager/fixtures/test_forms/registration/instances/blank_registration.xml').read()
    for key in values.keys():
        pattern = "#%s#" % key.upper()
        registration_xml_template = registration_xml_template.replace(pattern, values[key])
    return Instance(xml=registration_xml_template)


def load_simple_submission(custom_values):
    values = {
        'form_id': 'build_WaterSimple_1295821382',
        'name': 'Site Name',
        'value': '20',
        'device_id': '12345',
        'start_time': '2011-01-01T09:50:06.966',
        'end_time': '2011-01-01T09:53:22.965',
        'geopoint': '40.765102558006795 -73.97389419555664 300.0 4.0',
    }
    if 'start_time' in custom_values:
        st = custom_values['start_time']
        custom_values['start_time'] = st.strftime(XFORM_TIME_FORMAT)
        
        #if no end_time is specified, defaults to 1 hour
        values['end_time'] = datetime(st.year, st.month, st.day, st.hour+1).strftime(XFORM_TIME_FORMAT)
    
    if 'end_time' in custom_values:
        custom_values['end_time'] = custom_values['end_time'].strftime(XFORM_TIME_FORMAT)
    
    values.update(custom_values)
    subm = open("xform_manager/fixtures/test_forms/water_simple/instances/blank.xml").read()
    for key in values.keys():
        pattern = "#%s#" % key.upper()
        subm = subm.replace(pattern, values[key])
    return Instance(xml=subm)
