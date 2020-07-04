#!/usr/bin/env python

import unittest
from rdflib.term import Literal, URIRef
from os.path import abspath

from rml.io.sources import LogicalSource, RDFLogicalSource, MIMEType

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

class RDFLogicalSourceTests(unittest.TestCase):
    def test_iterator_rdfxml(self) -> None:
        """
        Test if we can iterate over every row using RDF XML
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.rdf',
                                       QUERY,
                                       MIMEType.RDF_XML)

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

    def test_iterator_jsonld(self) -> None:
        """
        Test if we can iterate over every row using JSON-LD
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.jsonld',
                                       QUERY,
                                       MIMEType.JSON_LD)

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

    def test_iterator_ntriples(self) -> None:
        """
        Test if we can iterate over every row
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.ntriples',
                                       QUERY,
                                       MIMEType.NTRIPLES)

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

    def test_iterator_turtle(self) -> None:
        """
        Test if we can iterate over every row
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.ttl',
                                       QUERY,
                                       MIMEType.TURTLE)

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

    def test_iterator_nquads(self) -> None:
        """
        Test if we can iterate over every row
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.nquads',
                                       CONJUCTIVE_QUERY,
                                       MIMEType.NQUADS)

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

    def test_iterator_trig(self) -> None:
        """
        Test if we can iterate over every row
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.trig',
                                       CONJUCTIVE_QUERY,
                                       MIMEType.TRIG)

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

    def test_iterator_trix(self) -> None:
        """
        Test if we can iterate over every row
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.trix',
                                       CONJUCTIVE_QUERY,
                                       MIMEType.TRIX)

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

    def test_iterator_n3(self) -> None:
        """
        Test if we can iterate over every row
        """
        source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.n3',
                                       QUERY,
                                       MIMEType.N3)

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

    def test_non_existing_file(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the input file
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            source: LogicalSource = RDFLogicalSource('this/file/does/not/exist',
                                           QUERY,
                                           MIMEType.RDF_XML)

    def test_rdf_xml_parsing_error(self) -> None:
        """
        Test if a ValueError exception is raised when the input file cannot be
        parsed.
        """
        with self.assertRaises(ValueError):
            source: LogicalSource = RDFLogicalSource('tests/assets/rdf/invalid.rdf',
                                           QUERY,
                                           MIMEType.RDF_XML)
    def test_jsonld_parsing_error(self) -> None:
        """
        Test if a ValueError exception is raised when the input file cannot be
        parsed.
        """
        with self.assertRaises(ValueError):
            source: LogicalSource = RDFLogicalSource('tests/assets/rdf/invalid.jsonld',
                                           QUERY,
                                           MIMEType.JSON_LD)

    def test_empty_iterator(self) -> None:
        """
        Test if we can handle an empty nput file
        """
        with self.assertRaises(StopIteration):
            source: LogicalSource = RDFLogicalSource('tests/assets/rdf/empty.rdf',
                                           QUERY,
                                           MIMEType.RDF_XML)
            next(source)

    def test_unknown_mimetype(self) -> None:
        """
        Test if a ValueError exception is raised when the MIME type is unknown.
        """
        with self.assertRaises(ValueError):
            source: LogicalSource = RDFLogicalSource('tests/assets/rdf/student.rdf',
                                           QUERY,
                                           MIMEType.UNKNOWN)
            next(source)

    def test_graph_access(self) -> None:
        """
        Test if the exposed graph contains triples.
        """
        source: RDFLogicalSource = RDFLogicalSource('tests/assets/rdf/student.rdf',
                                       QUERY,
                                       MIMEType.RDF_XML)
        self.assertGreater(len(source.graph), 0)



if __name__ == '__main__':
    unittest.main()
