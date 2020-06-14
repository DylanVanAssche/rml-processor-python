#!/usr/bin/env python

import unittest
from json.decoder import JSONDecodeError
from lxml.etree import XMLSyntaxError, XPathEvalError

from rml.sources import DCATLogicalSource

class DCATLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_non_existing_resource(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the resource
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/non-existing')

    def test_non_existing_url(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the url cannot be
        resolved
        """
        with self.assertRaises(FileNotFoundError):
            self.source = DCATLogicalSource('http://non-existing-url.be')

    def test_csv_iterator(self) -> None:
        """
        Test if we can iterate over every row of an CSV resource
        """
        self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/student.csv')
        self.assertDictEqual(next(self.source),
                             {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(self.source),
                             {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(self.source),
                             {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_csv_empty_iterator(self) -> None:
        """
        Test if we can handle an empty CSV file
        """
        with self.assertRaises(StopIteration):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/empty.csv')
            next(self.source)

    def test_csv_missing_header(self) -> None:
        """
        Test if we raise a ValueError when no CSV header is available
        """
        with self.assertRaises(ValueError):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/no_header.csv')

    def test_csv_delimiter(self) -> None:
        """
        Test if we can handle different delimiters such as TABS in TSV files.
        """
        self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/student.tsv',
                                       delimiter='\t')
        self.assertDictEqual(next(self.source),
                             {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(self.source),
                             {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(self.source),
                             {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_xml_iterator(self) -> None:
        """
        Test if we can iterate over every row of an XML resource
        """
        self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/xml/student.xml',
                                         reference_formulation='/students/student')

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

    def test_xml_invalid_xpath(self) -> None:
        """
        Test if we raise an XPathEvalError when the XPath expression is
        invalid
        """
        with self.assertRaises(XPathEvalError):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/xml/student.xml',
                                           reference_formulation='$$$')

    def test_xml_invalid_xml(self) -> None:
        """
        Test if we raise an XMLSyntaxError when the input file cannot be parsed
        as valid XML.
        """
        with self.assertRaises(XMLSyntaxError):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/xml/invalid.xml',
                                           reference_formulation='/students/student')

    def test_xml_empty_iterator(self) -> None:
        """
        Test if we can handle an empty iterator
        """
        self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/xml/student.xml',
                                       reference_formulation='/empty')
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_json_iterator(self) -> None:
        """
        Test if we can iterate over every row of a JSON resource
        """
        self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/json/student.json',
                                         reference_formulation='$.students.[*]')
        self.assertDictEqual(next(self.source),
                             {'id': '0', 'name': 'Herman', 'age': 65})
        self.assertDictEqual(next(self.source),
                             {'id': '1', 'name': 'Ann', 'age': 62})
        self.assertDictEqual(next(self.source),
                             {'id': '2', 'name': 'Simon', 'age': 23})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_json_invalid_jsonpath(self) -> None:
        """
        Test if we raise a ValueError when the JSONPath expression is invalid
        """
        with self.assertRaises(ValueError):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/json/student.json',
                                            reference_formulation='&$"£*W$')

    def test_json_invalid_json(self) -> None:
        """
        Test if we raise a JSONDecodeError when the input file cannot be parsed
        as valid JSON
        """
        with self.assertRaises(JSONDecodeError):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/json/invalid.json',
                                            reference_formulation='$.students.[*]')

    def test_json_empty_iterator(self) -> None:
        """
        Test if we handle an empty iterator
        """
        with self.assertRaises(StopIteration):
            self.source = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/json/student.json',
                                            reference_formulation='$.empty')
            next(self.source)

if __name__ == '__main__':
    unittest.main()
