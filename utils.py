#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
# import ipdb; ipdb.set_trace()

from xml.dom import minidom
import os, sys
from . import tag

SLASH = u"/"

class MyError(Exception):
    pass

def parse_xform_instance(xml_str):
    """
    'xml_str' is a str object holding the XML of an XForm
    instance. Return a python object representation of this XML file.
    """
    xml_obj = minidom.parseString(xml_str)
    root_node = xml_obj.documentElement

    # go through the xml object creating a corresponding python
    # object. note: we're immediately flattening out the document,
    # this is primarily because we haven't upgraded to Python 2.7, I'm
    # thinking OrderedDict could come in very handy here.
    xpath_counts = {}
    xpath_value_pairs = list(_xpath_value_pairs(root_node, xpath_counts))
    survey_data = {}
    for annotated_xpath, value in xpath_value_pairs:
        xpath_str = _xpath_str(annotated_xpath, xpath_counts)
        print annotated_xpath, xpath_str, value
        survey_data[xpath_str] = value

    assert len(list(_all_attributes(root_node)))==1, \
        u"There should be exactly one attribute in this document."
    survey_data.update({
            tag.XFORM_ID_STRING : root_node.getAttribute(u"id"),
            tag.INSTANCE_DOC_NAME : root_node.nodeName,
            })
    return survey_data

def _xpath(node):
    """
    Return a list describing this nodes full path (omitting the root
    node).
    """
    n = node
    levels = []
    while n.nodeType!=n.DOCUMENT_NODE:
        levels = [n.nodeName] + levels
        n = n.parentNode
    return levels[1:]

def _xpath_str(xpath_with_counts, xpath_counts):
    """
    Note: This must be called with the final xpath_counts. Go through
    an xpath with count annotations and return a string representation
    of this xpath. Something like 'a/b[0]/c'.
    """
    path = []
    for i in range(len(xpath_with_counts)):
        xpath_tuple = tuple([pair[0] for pair in xpath_with_counts[:i+1]])
        path.append(xpath_with_counts[i][0])
        if xpath_counts[xpath_tuple]>0:
            path[-1] += "[%s]" % xpath_with_counts[i][1]
    return SLASH.join(path)    

def _add_counts(xpath, xpath_counts):
    """
    Annotates an xpath with the current counts in xpath_counts.
    """
    return [(xpath[i], xpath_counts[tuple(xpath[:i+1])]) for i in range(len(xpath))]

def _update_xpath_counts(xpath, xpath_counts):
    """
    Add this xpath to the dictionary of xpath counts.
    """
    xpath_tuple = tuple(xpath)
    if xpath_tuple in xpath_counts: xpath_counts[xpath_tuple] += 1
    else: xpath_counts[xpath_tuple] = 0

def _xpath_value_pairs(node, xpath_counts):
    """
    Using a depth first traversal of the xml nodes build up a python
    object in parent that holds the tree structure of the data.
    """
    xpath = _xpath(node)
    _update_xpath_counts(xpath, xpath_counts)
    xpath_with_counts = _add_counts(xpath, xpath_counts)

    if len(node.childNodes)==0:
        # there's no data for this leaf node
        yield xpath_with_counts, None
    elif len(node.childNodes)==1 and \
            node.childNodes[0].nodeType==node.TEXT_NODE:
        # there is data for this leaf node
        yield xpath_with_counts, node.childNodes[0].nodeValue
    else:
        # this is an internal node
        for child in node.childNodes:
            for pair in _xpath_value_pairs(child, xpath_counts):
                yield pair

def _all_attributes(node):
    """
    Go through an XML document returning all the attributes we see.
    """
    if hasattr(node, "hasAttributes") and node.hasAttributes():
        for key in node.attributes.keys():
            yield key, node.getAttribute(key)
    for child in node.childNodes:
        for pair in _all_attributes(child):
            yield pair


# test = {"one/two" : 1, "one/three" : 3, "two" : 2}
# vardict = VariableDictionary(test)
# print vardict["one"]._d, vardict["two"]


class XFormParser(object):
    def __init__(self, xml):
        assert type(xml)==str or type(xml)==unicode, u"xml must be a string"
        self.doc = minidom.parseString(xml)
        self.root_node = self.doc.documentElement

    def get_variable_list(self):
        """
        Return a list of pairs [(path to variable1, attributes of variable1), ...].
        """
        bindings = self.doc.getElementsByTagName(u"bind")
        attributes = [dict(_all_attributes(b)) for b in bindings]
        # note: nodesets look like /water/source/blah we're returning source/blah
        return [(SLASH.join(d.pop(u"nodeset").split(SLASH)[2:]), d) for d in attributes]

    def get_variable_dictionary(self):
        d = {}
        for path, attributes in self.get_variable_list():
            assert path not in d, u"Paths should be unique."
            d[path] = attributes
        return d

    def follow(self, path):
        """
        Path is an array of node names. Starting at the document
        element we follow the path, returning the final node in the
        path.
        """
        element = self.doc.documentElement
        count = {}
        for name in path.split(SLASH):
            count[name] = 0
            for child in element.childNodes:
                if isinstance(child, minidom.Element) and child.tagName==name:
                    count[name] += 1
                    element = child
            assert count[name]==1
        return element

    def get_id_string(self):
        """
        Find the single child of h:head/model/instance and return the
        attribute 'id'.
        """
        instance = self.follow(u"h:head/model/instance")
        children = [child for child in instance.childNodes \
                        if isinstance(child, minidom.Element)]
        assert len(children)==1
        return children[0].getAttribute(u"id")

    def get_title(self):
        title = self.follow(u"h:head/h:title")
        assert len(title.childNodes)==1, u"There should be a single title"
        return title.childNodes[0].nodeValue

    supported_controls = ["input", "select1", "select", "upload"]

    def get_control_dict(self):
        def get_pairs(e):
            result = []
            if hasattr(e, "tagName") and e.tagName in self.supported_controls:
                result.append( (e.getAttribute("ref"),
                                get_text(follow(e, "label").childNodes)) )
            if e.hasChildNodes:
                for child in e.childNodes:
                    result.extend(get_pairs(child))
            return result
        return dict(get_pairs(self.follow("h:body")))


# f = open(sys.argv[1])
# xform = XFormParser(f.read())
# f.close()
# import json ; print json.dumps(xform.get_variable_dictionary(), indent=4)


from django.conf import settings
from django.core.mail import mail_admins
import traceback
def report_exception(subject, info, exc_info=None):
    if exc_info:
        cls, err = exc_info[:2]
        info += u"Exception in request: %s: %s" % (cls.__name__, err)
        info += u"".join(traceback.format_exception(*exc_info))

    if settings.DEBUG:
        print subject
        print info
    else:
        mail_admins(subject=subject, message=info)
        
from django.core.files.uploadedfile import InMemoryUploadedFile
def django_file(path, field_name, content_type):
    # adapted from here: http://groups.google.com/group/django-users/browse_thread/thread/834f988876ff3c45/
    f = open(path)
    return InMemoryUploadedFile(
        file=f,
        field_name=field_name,
        name=f.name,
        content_type=content_type,
        size=os.path.getsize(path),
        charset=None
        )
