#!/usr/bin/env python

import unittest
from lxml.etree import XMLSyntaxError, XPathEvalError

from rml.sources import XMLLogicalSource

class XMLLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator(self) -> None:
        self.source = XMLLogicalSource('/students/student', 'tests/assets/xml/student.xml')
        self.assertDictEqual(next(self.source),
                            {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(self.source),
                            {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(self.source),
                            {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.source = XMLLogicalSource('/students/student', 'this/file/does/not/exist')

    def test_invalid_xpath(self) -> None:
        with self.assertRaises(XPathEvalError):
            self.source = XMLLogicalSource('$$$', 'tests/assets/xml/student.xml')

    def test_invalid_xml(self) -> None:
        with self.assertRaises(XMLSyntaxError):
            self.source = XMLLogicalSource('/students/student', 'tests/assets/xml/invalid.xml')

    def test_empty_iterator(self) -> None:
        self.source = XMLLogicalSource('/empty', 'tests/assets/xml/student.xml')

if __name__ == '__main__':
    unittest.main()
