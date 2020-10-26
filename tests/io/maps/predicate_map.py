#!/usr/bin/env python

import unittest
from rdflib.term import URIRef
from lxml import etree

from rml.io.sources import MIMEType
from rml.io.maps import PredicateMap, ReferenceType
from rml.namespace import FOAF

XML_STUDENT_1 = """
    <student>
        <id>0</id>
        <name>Herman</name>
        <age>65</age>
    </student>
"""

XML_STUDENT_2 = """
    <student>
        <id>1</id>
        <name>Ann</name>
        <age>62</age>
    </student>
"""

XML_STUDENT_3 = """
    <student>
        <id>2</id>
        <name>Simon</name>
        <age>23</age>
    </student>
"""

class PredicateMapTests(unittest.TestCase):
    def test_unknown_termtype(self) -> None:
        """
        Test if we raise a ValueError when ReferenceType is unknown
        """
        with self.assertRaises(ValueError):
            sm = PredicateMap('http://example.com/{id}', ReferenceType.UNKNOWN,
                            MIMEType.CSV)
            sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_xml_constant(self) -> None:
        """
        Test if we can resolve a constant using XML data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.TEXT_XML)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj, FOAF.Person)

    def test_json_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_csv_constant(self) -> None:
        """
        Test if we can resolve a constant using CSV data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_tsv_constant(self) -> None:
        """
        Test if we can resolve a constant using TSV data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.TSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_sql_constant(self) -> None:
        """
        Test if we can resolve a constant using SQL data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.SQL)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_jsonld_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON-LD data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.JSON_LD)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_n3_constant(self) -> None:
        """
        Test if we can resolve a constant using N3 data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.N3)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_nquads_constant(self) -> None:
        """
        Test if we can resolve a constant using NQUADS data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.NQUADS)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_ntriples_constant(self) -> None:
        """
        Test if we can resolve a constant using NTRIPLES data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.NTRIPLES)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_rdf_constant(self) -> None:
        """
        Test if we can resolve a constant using RDF data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.RDF_XML)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_trig_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIG data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.TRIG)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_trix_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIX data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.TRIX)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_turtle_constant(self) -> None:
        """
        Test if we can resolve a constant using Turtle data
        """
        sm = PredicateMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                          MIMEType.TURTLE)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, FOAF.Person)

    def test_template(self) -> None:
        """
        Test if we can resolve a template using JSON data
        """
        sm = PredicateMap('{uri}', ReferenceType.TEMPLATE, MIMEType.JSON)
        subj = sm.resolve({'uri': 'http://example.com/me'})
        self.assertEqual(subj, URIRef('http://example.com/me'))

    def test_reference(self) -> None:
        """
        Test if we can resolve a reference using JSON data
        """
        sm = PredicateMap('uri', ReferenceType.REFERENCE, MIMEType.JSON)
        subj = sm.resolve({'uri': 'http://example.com/me'})
        self.assertEqual(subj, URIRef('http://example.com/me'))


if __name__ == '__main__':
    unittest.main()
