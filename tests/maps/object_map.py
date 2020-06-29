#!/usr/bin/env python

import unittest
from rdflib.term import URIRef, Literal
from lxml import etree

from rml.io.sources import MIMEType
from rml.io.maps import ObjectMap, TermType

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

XML_STUDENT_TITLE = """
    <student>
        <id>0</id>
        <name>Herman</name>
        <age>65</age>
        <title>King</title>
    </student>
"""

class ObjectMapTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def test_unknown_mimetype(self) -> None:
        """
        Test if we raise a ValueError when MIMEType is unknown
        """
        with self.assertRaises(ValueError):
            sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                            MIMEType.UNKNOWN)
            sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_unknown_termtype(self) -> None:
        """
        Test if we raise a ValueError when TermType is unknown
        """
        with self.assertRaises(ValueError):
            sm = ObjectMap('http://example.com/{id}', TermType.UNKNOWN,
                            MIMEType.CSV)
            sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_keyvalue_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using key-value
        """
        sm = ObjectMap('http://example.com/', TermType.TEMPLATE,
                        MIMEType.CSV)
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_jsonpath_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using key-value
        """
        sm = ObjectMap('http://example.com/', TermType.TEMPLATE,
                        MIMEType.CSV)
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_xpath_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using key-value
        """
        sm = ObjectMap('http://example.com/', TermType.TEMPLATE,
                        MIMEType.CSV)
        with self.assertRaises(NameError):
            subj = sm.resolve(etree.fromstring(XML_STUDENT_1))

    def test_keyvalue_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using key-value.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No subject may be generated when the reference does not exist.
        """
        sm = ObjectMap('title', TermType.REFERENCE,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(subj, URIRef('King'))

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_jsonpath_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using JSONPath.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No subject may be generated when the reference does not exist.
        """
        sm = ObjectMap('$.title', TermType.REFERENCE,
                        MIMEType.JSON)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(subj, URIRef('King'))

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_xpath_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using XPath.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No subject may be generated when the reference does not exist.
        """
        sm = ObjectMap('/student/title', TermType.REFERENCE,
                        MIMEType.TEXT_XML)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_TITLE))

        # Subject generated
        self.assertEqual(subj, URIRef('King'))

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve(etree.fromstring(XML_STUDENT_2))

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve(etree.fromstring(XML_STUDENT_3))

    def test_literal_template(self) -> None:
        """
        Test if we can resolve a literal template
        """
        sm = ObjectMap('http://example.com/{/student/id}', TermType.TEMPLATE,
                        MIMEType.TEXT_XML, is_iri=False)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj, Literal('http://example.com/0'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj, Literal('http://example.com/1'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj, Literal('http://example.com/2'))

    def test_literal_reference(self) -> None:
        """
        Test if we can resolve a literal reference
        """
        sm = ObjectMap('/student/name', TermType.REFERENCE,
                        MIMEType.TEXT_XML, is_iri=False)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj, Literal('Herman'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj, Literal('Ann'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj, Literal('Simon'))

    def test_xml_template(self) -> None:
        """
        Test if we can resolve an IRI template using XML data
        """
        sm = ObjectMap('http://example.com/{/student/id}', TermType.TEMPLATE,
                        MIMEType.TEXT_XML)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_xml_reference(self) -> None:
        """
        Test if we can resolve an IRI reference using XML data
        """
        sm = ObjectMap('/student/name', TermType.REFERENCE,
                        MIMEType.TEXT_XML)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj, URIRef('Simon'))


    def test_xml_constant(self) -> None:
        """
        Test if we can resolve a constant using XML data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.TEXT_XML)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_json_template(self) -> None:
        """
        Test if we can resolve a template using JSON data
        """
        sm = ObjectMap('http://example.com/{$.id}', TermType.TEMPLATE,
                        MIMEType.JSON)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_json_reference(self) -> None:
        """
        Test if we can resolve a reference using JSON data
        """
        sm = ObjectMap('$.name', TermType.REFERENCE,
                        MIMEType.JSON)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_json_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.JSON)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_csv_template(self) -> None:
        """
        Test if we can resolve a template using CSV data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_csv_reference(self) -> None:
        """
        Test if we can resolve a reference using CSV data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_csv_constant(self) -> None:
        """
        Test if we can resolve a constant using CSV data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_tsv_template(self) -> None:
        """
        Test if we can resolve a template using TSV data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.TSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_tsv_reference(self) -> None:
        """
        Test if we can resolve a reference using TSV data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.TSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_tsv_constant(self) -> None:
        """
        Test if we can resolve a constant using TSV data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.TSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_sql_template(self) -> None:
        """
        Test if we can resolve a template using SQL data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.SQL)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_sql_reference(self) -> None:
        """
        Test if we can resolve a reference using SQL data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.SQL)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_sql_constant(self) -> None:
        """
        Test if we can resolve a constant using SQL data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.SQL)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_jsonld_template(self) -> None:
        """
        Test if we can resolve a template using JSON-LD data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.JSON_LD)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_jsonld_reference(self) -> None:
        """
        Test if we can resolve a reference using JSON-LD data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.JSON_LD)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_jsonld_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON-LD data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.JSON_LD)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_n3_template(self) -> None:
        """
        Test if we can resolve a template using N3 data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.N3)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_n3_reference(self) -> None:
        """
        Test if we can resolve a reference using N3 data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.N3)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_n3_constant(self) -> None:
        """
        Test if we can resolve a constant using N3 data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.N3)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_nquads_template(self) -> None:
        """
        Test if we can resolve a template using NQUADS data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.NQUADS)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_nquads_reference(self) -> None:
        """
        Test if we can resolve a reference using NQUADS data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.NQUADS)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_nquads_constant(self) -> None:
        """
        Test if we can resolve a constant using NQUADS data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.NQUADS)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_ntriples_template(self) -> None:
        """
        Test if we can resolve a template using NTRIPLES data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.NTRIPLES)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_ntriples_reference(self) -> None:
        """
        Test if we can resolve a reference using NTRIPLES data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.NTRIPLES)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_ntriples_constant(self) -> None:
        """
        Test if we can resolve a constant using NTRIPLES data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.NTRIPLES)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_rdf_template(self) -> None:
        """
        Test if we can resolve a template using RDF data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.RDF_XML)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_rdf_reference(self) -> None:
        """
        Test if we can resolve a reference using RDF data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.RDF_XML)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_rdf_constant(self) -> None:
        """
        Test if we can resolve a constant using RDF data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.RDF_XML)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_trig_template(self) -> None:
        """
        Test if we can resolve a template using TRIG data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.TRIG)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_trig_reference(self) -> None:
        """
        Test if we can resolve a reference using TRIG data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.TRIG)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_trig_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIG data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.TRIG)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_trix_template(self) -> None:
        """
        Test if we can resolve a template using TRIX data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.TRIX)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_trix_reference(self) -> None:
        """
        Test if we can resolve a reference using TRIX data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.TRIX)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_trix_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIX data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.TRIX)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

    def test_turtle_template(self) -> None:
        """
        Test if we can resolve a template using Turtle data
        """
        sm = ObjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.TURTLE)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_turtle_reference(self) -> None:
        """
        Test if we can resolve a reference using turtle data
        """
        sm = ObjectMap('name', TermType.REFERENCE,
                        MIMEType.TURTLE)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_turtle_constant(self) -> None:
        """
        Test if we can resolve a constant using Turtle data
        """
        sm = ObjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.TURTLE)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

if __name__ == '__main__':
    unittest.main()
