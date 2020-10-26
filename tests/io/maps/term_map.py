#!/usr/bin/env python

import unittest
from rdflib.term import URIRef, Identifier
from lxml import etree
from lxml.etree import Element
from typing import Union, Dict

from rml.io.sources import MIMEType
from rml.io.maps import TermMap, ReferenceType
from rml.namespace import FOAF

XML_STUDENT = """
<student>
    <id>2</id>
    <name>Simon</name>
    <age></age>
</student>
"""


class MockTermMap(TermMap):
    def resolve(self, data: Union[Element, Dict]) -> Identifier:
        pass

class TermMapTests(unittest.TestCase):
    def test_invalid_xpath(self) -> None:
        """
        Test invalid XPath
        """
        with self.assertRaises(NameError):
            m = MockTermMap('term', ReferenceType.REFERENCE, MIMEType.TEXT_XML)
            result = m._resolve_reference('!@#%', etree.fromstring(XML_STUDENT))

    def test_invalid_jsonpath(self) -> None:
        """
        Test invalid JSONPath
        """
        with self.assertRaises(NameError):
            m = MockTermMap('term', ReferenceType.REFERENCE, MIMEType.JSON)
            result = m._resolve_reference('!@#%', {'id': 0, 'name': 'Herman'})

    def test_empty_result_xpath(self) -> None:
        """
        Test empty result XPath
        """
        with self.assertRaises(ResourceWarning):
            m = MockTermMap('age', ReferenceType.REFERENCE, MIMEType.TEXT_XML)
            result = m._resolve_reference('/student',
                                          etree.fromstring(XML_STUDENT))

    def test_empty_result_jsonpath(self) -> None:
        """
        Test empty result JSONPath
        """
        with self.assertRaises(ResourceWarning):
            m = MockTermMap('name', ReferenceType.REFERENCE, MIMEType.JSON)
            result = m._resolve_reference('$.name', {'id': 0, 'name': None})
