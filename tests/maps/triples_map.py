#!/usr/bin/env python

import unittest
from rdflib.term import URIRef, Literal
from rdflib import XSD, FOAF

from rml.io.sources import JSONLogicalSource, XMLLogicalSource, MIMEType
from rml.io.maps import SubjectMap, PredicateMap, ObjectMap, PredicateObjectMap, \
                     TriplesMap, TermType

class TriplesMapTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def test_json_generate_triple(self) -> None:
        """
        Test if we can generate a triple using JSON data.
        """
        ls = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.JSON)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        # Triple 1
        expected_result = [(URIRef('http://example.com/0'), \
                            FOAF.name, \
                            Literal('Herman'))]
        self.assertEqual(next(tm), expected_result)

        # Triple 2
        expected_result = [(URIRef('http://example.com/1'), \
                            FOAF.name, \
                            Literal('Ann'))]
        self.assertEqual(next(tm), expected_result)

        # Triple 3
        expected_result = [(URIRef('http://example.com/2'), \
                            FOAF.name, \
                            Literal('Simon'))]
        self.assertEqual(next(tm), expected_result)

        with self.assertRaises(StopIteration):
            next(tm)

    def test_json_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using JSON data.
        """
        ls = JSONLogicalSource('$.students.[*]',
                              'tests/assets/json/student.json')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.JSON)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        # Triples 1
        expected_result = [(URIRef('http://example.com/0'), \
                            FOAF.name, \
                            Literal('Herman')), \
                            (URIRef('http://example.com/0'), \
                             FOAF.age, \
                             Literal('65', datatype=XSD.integer))]
        self.assertEqual(next(tm), expected_result)

        # Triples 2
        expected_result = [(URIRef('http://example.com/1'), \
                            FOAF.name, \
                            Literal('Ann')),
                            (URIRef('http://example.com/1'), \
                             FOAF.age, \
                             Literal('62', datatype=XSD.integer))]
        self.assertEqual(next(tm), expected_result)

        # Triples 3
        expected_result = [(URIRef('http://example.com/2'), \
                            FOAF.name, \
                            Literal('Simon')),
                            (URIRef('http://example.com/2'), \
                             FOAF.age, \
                             Literal('23', datatype=XSD.integer))]
        self.assertEqual(next(tm), expected_result)

        with self.assertRaises(StopIteration):
            next(tm)

    def test_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using XML data.
        """
        ls = XMLLogicalSource('/students/student',
                               'tests/assets/xml/student.xml')
        sm = SubjectMap("http://example.com/{./id}", TermType.TEMPLATE,
                        MIMEType.TEXT_XML)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TEXT_XML)
        om = ObjectMap("./name", TermType.REFERENCE, MIMEType.TEXT_XML,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        # Triple 1
        expected_result = [(URIRef('http://example.com/0'), \
                            FOAF.name, \
                            Literal('Herman'))]
        self.assertEqual(next(tm), expected_result)

        # Triple 2
        expected_result = [(URIRef('http://example.com/1'), \
                            FOAF.name, \
                            Literal('Ann'))]
        self.assertEqual(next(tm), expected_result)

        # Triple 3
        expected_result = [(URIRef('http://example.com/2'), \
                            FOAF.name, \
                            Literal('Simon'))]
        self.assertEqual(next(tm), expected_result)

        with self.assertRaises(StopIteration):
            next(tm)

    def test_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using XML data.
        """
        ls = XMLLogicalSource('/students/student',
                              'tests/assets/xml/student.xml')
        sm = SubjectMap("http://example.com/{./id}", TermType.TEMPLATE,
                        MIMEType.TEXT_XML)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TEXT_XML)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TEXT_XML)
        om1 = ObjectMap("./name", TermType.REFERENCE, MIMEType.TEXT_XML,
                        is_iri=False)
        om2 = ObjectMap("./age", TermType.REFERENCE, MIMEType.TEXT_XML,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        # Triples 1
        expected_result = [(URIRef('http://example.com/0'), \
                            FOAF.name, \
                            Literal('Herman')), \
                            (URIRef('http://example.com/0'), \
                             FOAF.age, \
                             Literal('65'))]
        self.assertEqual(next(tm), expected_result)

        # Triples 2
        expected_result = [(URIRef('http://example.com/1'), \
                            FOAF.name, \
                            Literal('Ann')),
                            (URIRef('http://example.com/1'), \
                             FOAF.age, \
                             Literal('62'))]
        self.assertEqual(next(tm), expected_result)

        # Triples 3
        expected_result = [(URIRef('http://example.com/2'), \
                            FOAF.name, \
                            Literal('Simon')),
                            (URIRef('http://example.com/2'), \
                             FOAF.age, \
                             Literal('23'))]
        self.assertEqual(next(tm), expected_result)

        with self.assertRaises(StopIteration):
            next(tm)
