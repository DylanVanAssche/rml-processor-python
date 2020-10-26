#!/usr/bin/env python

import unittest
from json.decoder import JSONDecodeError
from lxml.etree import XMLSyntaxError, XPathEvalError
from rdflib.term import Literal, URIRef
from os import environ
from os.path import abspath

from rml.io.sources import DCATLogicalSource, MIMEType

# Resolve RDF file to absolute path for SPARQL
student_rdf_path = abspath('tests/assets/rdf/student.rdf')
CONJUCTIVE_QUERY="""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?person ?name ?age
FROM <file://""" + student_rdf_path + """>
WHERE {
    ?person foaf:name ?name .
    ?person foaf:age ?age .
}
ORDER BY DESC(?age)
"""

QUERY="""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?person ?name ?age
WHERE {
    ?person foaf:name ?name .
    ?person foaf:age ?age .
}
ORDER BY DESC(?age)
"""
HOST = environ['HOST']


class DCATLogicalSourceTests(unittest.TestCase):
    def _assert_rdf(self, source: DCATLogicalSource) -> None:
        student = next(source)
        self.assertEqual(student['person'], URIRef('http://example.com/0'))
        self.assertEqual(student['name'], Literal('Herman'))
        self.assertEqual(student['age'], Literal('65'))

        student = next(source)
        self.assertEqual(student['person'], URIRef('http://example.com/1'))
        self.assertEqual(student['name'], Literal('Ann'))
        self.assertEqual(student['age'], Literal('62'))

        student = next(source)
        self.assertEqual(student['person'], URIRef('http://example.com/2'))
        self.assertEqual(student['name'], Literal('Simon'))
        self.assertEqual(student['age'], Literal('23'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_non_existing_resource(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the resource
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            source = DCATLogicalSource(f'http://{HOST}:8000/non-existing',
                                       MIMEType.TEXT_XML)

    def test_unknown_format(self) -> None:
        """
        Test if a ValueError exception when the format is not supported.
        """
        with self.assertRaises(ValueError):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.csv',
                                       MIMEType.UNKNOWN)

    def test_non_existing_url(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the url cannot be
        resolved
        """
        with self.assertRaises(FileNotFoundError):
            source = DCATLogicalSource('http://non-existing-url.be',
                                       MIMEType.TEXT_XML)

    def test_mime_type(self) -> None:
        """
        Test the MIME type property
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.csv',
                                   MIMEType.CSV)
        self.assertEqual(source.mime_type, MIMEType.CSV)

    def test_csv_iterator(self) -> None:
        """
        Test if we can iterate over every row of an CSV resource
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.csv',
                                   MIMEType.CSV)
        self.assertDictEqual(next(source), {'id': '0', 'name': 'Herman',
                                            'age': '65', 'iri': 'http://example.com/myStudent1'})
        self.assertDictEqual(next(source), {'id': '1', 'name': 'Ann',
                                            'age': '62', 'iri': 'http://example.com/myStudent2'})
        self.assertDictEqual(next(source), {'id': '2', 'name': 'Simon',
                                            'age': '23', 'iri': 'http://example.com/myStudent3'})
        with self.assertRaises(StopIteration):
            next(source)

    def test_csv_empty_iterator(self) -> None:
        """
        Test if we can handle an empty CSV file
        """
        with self.assertRaises(StopIteration):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/empty.csv',
                                       MIMEType.CSV)
            next(source)

    def test_csv_missing_header(self) -> None:
        """
        Test if we raise a ValueError when no CSV header is available
        """
        with self.assertRaises(ValueError):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/no_header.csv',
                                       MIMEType.CSV)
            next(source)

    def test_csv_delimiter(self) -> None:
        """
        Test if we can handle different delimiters such as TABS in TSV files.
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.tsv',
                                   MIMEType.TSV, delimiter='\t')
        self.assertDictEqual(next(source),
                             {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(source),
                             {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(source),
                             {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(source)

    def test_xml_iterator(self) -> None:
        """
        Test if we can iterate over every row of an XML resource
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/xml/student.xml',
                                   MIMEType.APPLICATION_XML,
                                   rml_iterator='/students/student')
        student = next(source)
        self.assertEqual(student.xpath('./id')[0].text, '0')
        self.assertEqual(student.xpath('./name')[0].text, 'Herman')
        self.assertEqual(student.xpath('./age')[0].text, '65')

        student = next(source)
        self.assertEqual(student.xpath('./id')[0].text, '1')
        self.assertEqual(student.xpath('./name')[0].text, 'Ann')
        self.assertEqual(student.xpath('./age')[0].text, '62')

        student = next(source)
        self.assertEqual(student.xpath('./id')[0].text, '2')
        self.assertEqual(student.xpath('./name')[0].text, 'Simon')
        self.assertEqual(student.xpath('./age')[0].text, '23')

        with self.assertRaises(StopIteration):
            next(source)

    def test_xml_invalid_xpath(self) -> None:
        """
        Test if we raise an XPathEvalError when the XPath expression is
        invalid
        """
        with self.assertRaises(NameError):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/xml/student.xml',
                                       MIMEType.APPLICATION_XML,
                                       rml_iterator='$$$')

    def test_xml_invalid_xml(self) -> None:
        """
        Test if we raise an XMLSyntaxError when the input file cannot be parsed
        as valid XML.
        """
        with self.assertRaises(XMLSyntaxError):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/xml/invalid.xml',
                                       MIMEType.APPLICATION_XML,
                                       rml_iterator='/students/student')

    def test_xml_empty_iterator(self) -> None:
        """
        Test if we can handle an empty iterator
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/xml/student.xml',
                                   MIMEType.APPLICATION_XML,
                                   rml_iterator='/empty')
        with self.assertRaises(StopIteration):
            next(source)

    def test_json_iterator(self) -> None:
        """
        Test if we can iterate over every row of a JSON resource
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/json/student.json',
                                   MIMEType.JSON,
                                   rml_iterator='$.students.[*]')
        self.assertDictEqual(next(source),
                             {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(source),
                             {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(source),
                             {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(source)

    def test_json_invalid_jsonpath(self) -> None:
        """
        Test if we raise a ValueError when the JSONPath expression is invalid
        """
        with self.assertRaises(ValueError):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/json/student.json',
                                       MIMEType.JSON,
                                       rml_iterator='&$"£*W$')

    def test_json_invalid_json(self) -> None:
        """
        Test if we raise a JSONDecodeError when the input file cannot be parsed
        as valid JSON
        """
        with self.assertRaises(JSONDecodeError):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/json/invalid.json',
                                       MIMEType.JSON,
                                       rml_iterator='$.students.[*]')

    def test_json_empty_iterator(self) -> None:
        """
        Test if we handle an empty iterator
        """
        with self.assertRaises(StopIteration):
            source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/json/student.json',
                                       MIMEType.JSON,
                                       rml_iterator='$.empty')
            next(source)

    def test_iterator_rdfxml(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.rdf',
                                   MIMEType.RDF_XML,
                                   rml_iterator=QUERY)
        self._assert_rdf(source)


    def test_iterator_jsonld(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.jsonld',
                                   MIMEType.JSON_LD,
                                   rml_iterator=QUERY)
        self._assert_rdf(source)

    def test_iterator_ntriples(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.ntriples',
                                   MIMEType.NTRIPLES,
                                   rml_iterator=QUERY)
        self._assert_rdf(source)

    def test_iterator_turtle(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.ttl',
                                   MIMEType.TURTLE,
                                   rml_iterator=QUERY)
        self._assert_rdf(source)

    def test_iterator_nquads(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.nquads',
                                   MIMEType.NQUADS,
                                   rml_iterator=CONJUCTIVE_QUERY)
        self._assert_rdf(source)

    def test_iterator_trig(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.trig',
                                   MIMEType.TRIG,
                                   rml_iterator=CONJUCTIVE_QUERY)
        self._assert_rdf(source)

    def test_iterator_trix(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.trix',
                                   MIMEType.TRIX,
                                   rml_iterator=CONJUCTIVE_QUERY)
        self._assert_rdf(source)

    def test_iterator_n3(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.n3',
                                   MIMEType.N3,
                                   rml_iterator=QUERY)
        self._assert_rdf(source)


if __name__ == '__main__':
    unittest.main()
