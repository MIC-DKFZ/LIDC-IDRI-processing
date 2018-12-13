# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 12:28:19 2018

@author: m.goetz@dkfz-heidelberg.de
"""
import xml.etree.ElementTree as ET

def create_xml_tree(filepath):
    """
    Method to ignore the namespaces if ElementTree is used. 
    Necessary becauseElementTree, by default, extend
    Tag names by the name space, but the namespaces used in the
    LIDC-IDRI dataset are not consistent. 
    Solution based on https://stackoverflow.com/questions/13412496/python-elementtree-module-how-to-ignore-the-namespace-of-xml-files-to-locate-ma
    
    instead of ET.fromstring(xml)
    """
    it = ET.iterparse(filepath)
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        for at in el.attrib.keys(): # strip namespaces of attributes too
            if '}' in at:
                newat = at.split('}', 1)[1]
                el.attrib[newat] = el.attrib[at]
                del el.attrib[at]
    return it.root
        
def get_study_uid(root):
    result=None
    try:
        result=root.find("ResponseHeader/StudyInstanceUID").text
    except:
        pass
    return result

def get_series_uid(root):
    result=None
    try:
        result=root.find("ResponseHeader/SeriesInstanceUid").text
    except:
        pass
    return result

def read_nodule_property(nodule_tree, tag):
    """
    Reading a specified propertiy of a nodule. If the property is not specified
    in the corresponding part of the xml tree (nodule_tree), -1 is returned.
    """
    try:
        result=str(nodule_tree.find("characteristics/"+tag).text)
        return result
    except:
        return str(-1)