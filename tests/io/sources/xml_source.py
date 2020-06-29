#!/usr/bin/env python

import unittest
from lxml.etree import XMLSyntaxError, XPathEvalError
from lxml import etree

from rml.io.sources import XMLLogicalSource

class XMLLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator(self) -> None:
        """
        Test if we can iterate over each XML element
        """
        self.source = XMLLogicalSource('/students/student', 'tests/assets/xml/student.xml')

        student = next(self.source)
        self.assertEqual(student.xpath('./id')[0].text, '0')
        self.assertEqual(student.xpath('./name')[0].text, 'Herman')
        self.assertEqual(student.xpath('./age')[0].text, '65')

        student = next(self.source)
        self.assertEqual(student.xpath('./id')[0].text, '1')
        self.assertEqual(student.xpath('./name')[0].text, 'Ann')
        self.assertEqual(student.xpath('./age')[0].text, '62')

        student = next(self.source)
        self.assertEqual(student.xpath('./id')[0].text, '2')
        self.assertEqual(student.xpath('./name')[0].text, 'Simon')
        self.assertEqual(student.xpath('./age')[0].text, '23')

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_file(self) -> None:
        """
        Test if we raise a FileNotFoundError exception when the input file does
        not exist
        """
        with self.assertRaises(FileNotFoundError):
            self.source = XMLLogicalSource('/students/student', 'this/file/does/not/exist')

    def test_invalid_xpath(self) -> None:
        """
        Test if we raise an XPathEvalError when the XPath expression is
        invalid
        """
        with self.assertRaises(XPathEvalError):
            self.source = XMLLogicalSource('$$$', 'tests/assets/xml/student.xml')

    def test_invalid_xml(self) -> None:
        """
        Test if we raise an XMLSyntaxError when the input file cannot be parsed
        as valid XML.
        """
        with self.assertRaises(XMLSyntaxError):
            self.source = XMLLogicalSource('/students/student', 'tests/assets/xml/invalid.xml')

    def test_empty_iterator(self) -> None:
        """
        Test if we can handle an empty iterator
        """
        self.source = XMLLogicalSource('/empty', 'tests/assets/xml/student.xml')
        with self.assertRaises(StopIteration):
            next(self.source)

if __name__ == '__main__':
    unittest.main()
