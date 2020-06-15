#!/usr/bin/env python

import unittest
from rdflib.term import Literal, URIRef

from rml.sources import RDFLogicalSource

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
                                       QUERY)

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
                                           QUERY)

    def test_empty_iterator(self) -> None:
        """
        Test if we can handle an empty nput file
        """
        with self.assertRaises(StopIteration):
            self.source = RDFLogicalSource('tests/assets/rdf/empty.rdf',
                                           QUERY)
            next(self.source)

if __name__ == '__main__':
    unittest.main()
