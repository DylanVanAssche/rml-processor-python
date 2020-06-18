#!/usr/bin/env python

import unittest
from rdflib.term import Literal, URIRef

from rml.sources import RDFLogicalSource, MIMEType

CONJUCTIVE_QUERY="""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?person ?name ?age
FROM <file:///home/dylan/Projects/rml-blocks/tests/assets/rdf/student.rdf>
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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator_rdfxml(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.rdf',
                                       QUERY,
                                       MIMEType.RDF_XML)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_iterator_jsonld(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.jsonld',
                                       QUERY,
                                       MIMEType.JSON_LD)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_iterator_ntriples(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.ntriples',
                                       QUERY,
                                       MIMEType.NTRIPLES)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_iterator_turtle(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.ttl',
                                       QUERY,
                                       MIMEType.TURTLE)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_iterator_nquads(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.nquads',
                                       CONJUCTIVE_QUERY,
                                       MIMEType.NQUADS)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_iterator_trig(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.trig',
                                       CONJUCTIVE_QUERY,
                                       MIMEType.TRIG)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_iterator_trix(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.trix',
                                       CONJUCTIVE_QUERY,
                                       MIMEType.TRIX)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_iterator_n3(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = RDFLogicalSource('tests/assets/rdf/student.n3',
                                       QUERY,
                                       MIMEType.N3)

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#0'))
        self.assertEqual(student_name, Literal('Herman'))
        self.assertEqual(student_age, Literal('65'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#1'))
        self.assertEqual(student_name, Literal('Ann'))
        self.assertEqual(student_age, Literal('62'))

        student, student_name, student_age = next(self.source)
        self.assertEqual(student, URIRef('http://example.com/student/#2'))
        self.assertEqual(student_name, Literal('Simon'))
        self.assertEqual(student_age, Literal('23'))

        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_file(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the input file
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            self.source = RDFLogicalSource('this/file/does/not/exist',
                                           QUERY,
                                           MIMEType.RDF_XML)

    def test_empty_iterator(self) -> None:
        """
        Test if we can handle an empty nput file
        """
        with self.assertRaises(StopIteration):
            self.source = RDFLogicalSource('tests/assets/rdf/empty.rdf',
                                           QUERY,
                                           MIMEType.RDF_XML)
            next(self.source)

if __name__ == '__main__':
    unittest.main()
