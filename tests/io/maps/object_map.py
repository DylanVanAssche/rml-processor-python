#!/usr/bin/env python

import unittest
from rdflib.term import URIRef, Literal
from lxml import etree

from rml.io.sources import MIMEType
from rml.io.maps import ObjectMap, ReferenceType
from rml.namespace import FOAF, XSD

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
    def test_unknown_mimetype(self) -> None:
        """
        Test if we raise a ValueError when MIMEType is unknown
        """
        with self.assertRaises(ValueError):
            om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                            MIMEType.UNKNOWN, is_iri=True)
            om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_unknown_termtype(self) -> None:
        """
        Test if we raise a ValueError when ReferenceType is unknown
        """
        with self.assertRaises(ValueError):
            om = ObjectMap('http://example.com/{id}', ReferenceType.UNKNOWN,
                            MIMEType.CSV, is_iri=True)
            om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_keyvalue_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using key-value
        """
        om = ObjectMap('http://example.com/', ReferenceType.TEMPLATE,
                        MIMEType.CSV, is_iri=True)
        with self.assertRaises(NameError):
            obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_jsonpath_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using JSONPath
        """
        om = ObjectMap('http://example.com/', ReferenceType.TEMPLATE,
                        MIMEType.JSON, is_iri=True)
        with self.assertRaises(NameError):
            obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_xpath_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using XML
        """
        om = ObjectMap('http://example.com/', ReferenceType.TEMPLATE,
                       MIMEType.TEXT_XML, is_iri=True)
        with self.assertRaises(NameError):
            obj = om.resolve(etree.fromstring(XML_STUDENT_1))

    def test_keyvalue_tabular_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using key-value
        tabular.
        Since the header specifies which columns need to be provided, a missing
        column raises an error.
        In this test case, only the first row has a valid value, others are
        NULL. No object may be generated when the reference does not exist.
        """
        om = ObjectMap('title', ReferenceType.REFERENCE, MIMEType.CSV, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(obj, Literal('King'))

        # No object generated
        with self.assertRaises(NameError):
            obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No object generated
        with self.assertRaises(NameError):
            obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_keyvalue_nontabular_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using key-value non
        tabular.
        This can happen when a certain column has NULL values, the data schema
        is not fixed for these data formats in comparison to tabular data.
        In this test case, only the first row has a valid value, others are
        NULL. No object may be generated when the reference does not exist.
        """
        om = ObjectMap('title', ReferenceType.REFERENCE, MIMEType.RDF_XML,
                       is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(obj, Literal('King'))

        # No object generated
        with self.assertRaises(ResourceWarning):
            obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No object generated
        with self.assertRaises(ResourceWarning):
            obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_jsonpath_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using JSONPath.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No object may be generated when the reference does not exist.
        """
        om = ObjectMap('$.title', ReferenceType.REFERENCE, MIMEType.JSON,
                       is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(obj, Literal('King'))

        # No object generated
        with self.assertRaises(ResourceWarning):
            obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No object generated
        with self.assertRaises(ResourceWarning):
            obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_xpath_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using XPath.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No object may be generated when the reference does not exist.
        """
        om = ObjectMap('/student/title', ReferenceType.REFERENCE,
                        MIMEType.TEXT_XML, is_iri=False)
        obj = om.resolve(etree.fromstring(XML_STUDENT_TITLE))

        # Subject generated
        self.assertEqual(obj, Literal('King'))

        # No object generated
        with self.assertRaises(ResourceWarning):
            obj = om.resolve(etree.fromstring(XML_STUDENT_2))

        # No object generated
        with self.assertRaises(ResourceWarning):
            obj = om.resolve(etree.fromstring(XML_STUDENT_3))

    def test_literal_template(self) -> None:
        """
        Test if we can resolve a literal template
        """
        om = ObjectMap('http://example.com/{/student/id}', ReferenceType.TEMPLATE,
                        MIMEType.TEXT_XML, is_iri=False)
        obj = om.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(obj, Literal('http://example.com/0'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(obj, Literal('http://example.com/1'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(obj, Literal('http://example.com/2'))

    def test_literal_reference(self) -> None:
        """
        Test if we can resolve a literal reference
        """
        om = ObjectMap('/student/name', ReferenceType.REFERENCE,
                       MIMEType.TEXT_XML, is_iri=False)
        obj = om.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(obj, Literal('Simon'))

    def test_literal_language(self) -> None:
        """
        Test if we can generate a Literal with a given language tag.
        """
        om = ObjectMap('/student/name', ReferenceType.REFERENCE,
                       MIMEType.TEXT_XML, language='en-us', is_iri=False)
        obj = om.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(obj, Literal('Herman', lang='en-us'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(obj, Literal('Ann', lang='en-us'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(obj, Literal('Simon', lang='en-us'))

    def test_literal_datatype(self) -> None:
        """
        Test if we can generate a Literal with a given datatype.
        """
        om = ObjectMap('/student/name', ReferenceType.REFERENCE,
                       MIMEType.TEXT_XML, datatype=XSD.string, is_iri=False)
        obj = om.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(obj, Literal('Herman', datatype=XSD.string))
        obj = om.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(obj, Literal('Ann', datatype=XSD.string))
        obj = om.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(obj, Literal('Simon', datatype=XSD.string))

    def test_literal_error_both(self) -> None:
        """
        Test if we raise a TypeError when a language tag and datatype are
        specified when generating a Literal.
        """
        with self.assertRaises(TypeError):
            om = ObjectMap('/student/name', ReferenceType.REFERENCE,
                           MIMEType.TEXT_XML, datatype=XSD.string,
                           language='en-us', is_iri=False)
            obj = om.resolve(etree.fromstring(XML_STUDENT_1))

    def test_invalid_lang_tag(self) -> None:
        """
        Test if we raise a ValueError when an invalid language tag is specified
        when generating a Literal.
        """
        with self.assertRaises(ValueError):
            om = ObjectMap('/student/name', ReferenceType.REFERENCE,
                           MIMEType.TEXT_XML, language='$£WDSD', is_iri=False)
            obj = om.resolve(etree.fromstring(XML_STUDENT_1))

    def test_xml_template(self) -> None:
        """
        Test if we can resolve an IRI template using XML data
        """
        om = ObjectMap('http://example.com/{/student/id}', ReferenceType.TEMPLATE,
                        MIMEType.TEXT_XML, is_iri=True)
        obj = om.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_xml_reference(self) -> None:
        """
        Test if we can resolve an IRI reference using XML data
        """
        om = ObjectMap('/student/name', ReferenceType.REFERENCE,
                        MIMEType.TEXT_XML, is_iri=False)
        obj = om.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(obj, Literal('Simon'))


    def test_xml_constant(self) -> None:
        """
        Test if we can resolve a constant using XML data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.TEXT_XML, is_iri=True)
        obj = om.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(obj, FOAF.Person)

    def test_json_template(self) -> None:
        """
        Test if we can resolve a template using JSON data
        """
        om = ObjectMap('http://example.com/{$.id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_json_reference(self) -> None:
        """
        Test if we can resolve a reference using JSON data
        """
        om = ObjectMap('$.name', ReferenceType.REFERENCE,
                        MIMEType.JSON, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_json_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.JSON, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_csv_template(self) -> None:
        """
        Test if we can resolve a template using CSV data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.CSV, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_csv_reference(self) -> None:
        """
        Test if we can resolve a reference using CSV data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.CSV, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_csv_constant(self) -> None:
        """
        Test if we can resolve a constant using CSV data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.CSV, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_tsv_template(self) -> None:
        """
        Test if we can resolve a template using TSV data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                       MIMEType.TSV, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_tsv_reference(self) -> None:
        """
        Test if we can resolve a reference using TSV data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                       MIMEType.TSV, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_tsv_constant(self) -> None:
        """
        Test if we can resolve a constant using TSV data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.TSV, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_sql_template(self) -> None:
        """
        Test if we can resolve a template using SQL data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.SQL, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_sql_reference(self) -> None:
        """
        Test if we can resolve a reference using SQL data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.SQL, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_sql_constant(self) -> None:
        """
        Test if we can resolve a constant using SQL data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.SQL, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_jsonld_template(self) -> None:
        """
        Test if we can resolve a template using JSON-LD data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON_LD, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_jsonld_reference(self) -> None:
        """
        Test if we can resolve a reference using JSON-LD data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.JSON_LD, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_jsonld_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON-LD data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.JSON_LD, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_n3_template(self) -> None:
        """
        Test if we can resolve a template using N3 data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.N3, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_n3_reference(self) -> None:
        """
        Test if we can resolve a reference using N3 data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.N3, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_n3_constant(self) -> None:
        """
        Test if we can resolve a constant using N3 data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.N3, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_nquads_template(self) -> None:
        """
        Test if we can resolve a template using NQUADS data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.NQUADS, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_nquads_reference(self) -> None:
        """
        Test if we can resolve a reference using NQUADS data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.NQUADS, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_nquads_constant(self) -> None:
        """
        Test if we can resolve a constant using NQUADS data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.NQUADS, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_ntriples_template(self) -> None:
        """
        Test if we can resolve a template using NTRIPLES data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.NTRIPLES, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_ntriples_reference(self) -> None:
        """
        Test if we can resolve a reference using NTRIPLES data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.NTRIPLES, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_ntriples_constant(self) -> None:
        """
        Test if we can resolve a constant using NTRIPLES data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.NTRIPLES, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_rdf_template(self) -> None:
        """
        Test if we can resolve a template using RDF data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.RDF_XML, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_rdf_reference(self) -> None:
        """
        Test if we can resolve a reference using RDF data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.RDF_XML, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_rdf_constant(self) -> None:
        """
        Test if we can resolve a constant using RDF data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.RDF_XML, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_trig_template(self) -> None:
        """
        Test if we can resolve a template using TRIG data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.TRIG, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_trig_reference(self) -> None:
        """
        Test if we can resolve a reference using TRIG data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.TRIG, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_trig_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIG data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.TRIG, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_trix_template(self) -> None:
        """
        Test if we can resolve a template using TRIX data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.TRIX, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_trix_reference(self) -> None:
        """
        Test if we can resolve a reference using TRIX data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.TRIX, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_trix_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIX data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.TRIX, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_turtle_template(self) -> None:
        """
        Test if we can resolve a template using Turtle data
        """
        om = ObjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.TURTLE, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, URIRef('http://example.com/0'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, URIRef('http://example.com/1'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, URIRef('http://example.com/2'))

    def test_turtle_reference(self) -> None:
        """
        Test if we can resolve a reference using turtle data
        """
        om = ObjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.TURTLE, is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, Literal('Herman'))
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, Literal('Ann'))
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, Literal('Simon'))

    def test_turtle_constant(self) -> None:
        """
        Test if we can resolve a constant using Turtle data
        """
        om = ObjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                       MIMEType.TURTLE, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(obj, FOAF.Person)
        obj = om.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(obj, FOAF.Person)

    def test_convert_sql_datetime(self) -> None:
        """
        Test if a SQL datetime is converted to XSD.dateTime.
        """
        om = ObjectMap('datetime', ReferenceType.REFERENCE, MIMEType.TURTLE,
                       is_iri=False, datatype=XSD.dateTime)
        obj = om.resolve({'datetime': '2020-04-22 14:55:66'})
        print(obj)
        self.assertEqual(obj, Literal('2020-04-22T14:55:66',
                                      datatype=XSD.dateTime))

    def test_reference_iri(self) -> None:
        """
        Test the generation of an object using a reference as an IRI.
        """
        om = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.TURTLE, is_iri=True)
        obj = om.resolve({'id': '0', 'name': 'http://example.com/Herman'})
        self.assertEqual(obj, URIRef('http://example.com/Herman'))

    def test_constant_literal(self) -> None:
        """
        Test the generation of an object using a constant as Literal.
        """
        om = ObjectMap('myConstant', ReferenceType.CONSTANT, MIMEType.TURTLE,
                       is_iri=False)
        obj = om.resolve({'id': '0', 'name': 'http://example.com/Herman'})
        self.assertEqual(obj, Literal('myConstant'))


if __name__ == '__main__':
    unittest.main()
