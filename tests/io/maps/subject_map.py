#!/usr/bin/env python

import unittest
from rdflib.term import URIRef, BNode
from lxml import etree

from rml.io.sources import MIMEType
from rml.io.maps import SubjectMap, ReferenceType
from rml.namespace import FOAF, R2RML

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

class SubjectMapTests(unittest.TestCase):
    def _check_template_kv(self, sm: SubjectMap) -> None:
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj[0], URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj[0], URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj[0], URIRef('http://example.com/2'))

    def _check_reference_kv(self, sm: SubjectMap) -> None:
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj[0], URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj[0], URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj[0], URIRef('Simon'))

    def _check_constant_kv(self, sm: SubjectMap) -> None:
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj[0], FOAF.Person)
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj[0], FOAF.Person)
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj[0], FOAF.Person)

    def test_unknown_mimetype(self) -> None:
        """
        Test if we raise a ValueError when MIMEType is unknown
        """
        with self.assertRaises(ValueError):
            sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                            MIMEType.UNKNOWN, None, None)
            sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_unknown_termtype(self) -> None:
        """
        Test if we raise a ValueError when ReferenceType is unknown
        """
        with self.assertRaises(ValueError):
            sm = SubjectMap('http://example.com/{id}', ReferenceType.UNKNOWN,
                            MIMEType.CSV, None, None)
            sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_keyvalue_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using key-value
        """
        sm = SubjectMap('http://example.com/', ReferenceType.TEMPLATE,
                        MIMEType.CSV, None, None)
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_jsonpath_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using key-value
        """
        sm = SubjectMap('http://example.com/', ReferenceType.TEMPLATE,
                        MIMEType.CSV, None, None)
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_xpath_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using key-value
        """
        sm = SubjectMap('http://example.com/', ReferenceType.TEMPLATE,
                        MIMEType.CSV, None, None)
        with self.assertRaises(NameError):
            subj = sm.resolve(etree.fromstring(XML_STUDENT_1))

    def test_keyvalue_tabular_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using key-value
        tabular.
        This can happen when a certain column doesn't exist
        In this test case, the first row is valid while the next ones are
        missing a column. In case of tabular data, the columns cannot be
        missing if they are present in the header.
        """
        sm = SubjectMap('title', ReferenceType.REFERENCE,
                        MIMEType.CSV, R2RML.IRI, None)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(subj[0], URIRef('King'))

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_keyvalue_nontabular_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using key-value
        tabular data.
        This can happen when a certain reference has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No subject may be generated when the reference does not exist.
        """
        sm = SubjectMap('title', ReferenceType.REFERENCE,
                        MIMEType.RDF_XML, R2RML.IRI, None)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(subj[0], URIRef('King'))

        # No subject generated
        with self.assertRaises(ResourceWarning):
            subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No subject generated
        with self.assertRaises(ResourceWarning):
            subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_jsonpath_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using JSONPath.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No subject may be generated when the reference does not exist.
        """
        sm = SubjectMap('$.title', ReferenceType.REFERENCE,
                MIMEType.JSON, R2RML.IRI, None)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(subj[0], URIRef('King'))

        # No subject generated
        with self.assertRaises(ResourceWarning):
            subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No subject generated
        with self.assertRaises(ResourceWarning):
            subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_xpath_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using XPath.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No subject may be generated when the reference does not exist.
        """
        sm = SubjectMap('/student/title', ReferenceType.REFERENCE,
                        MIMEType.TEXT_XML, R2RML.IRI, None)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_TITLE))

        # Subject generated
        self.assertEqual(subj[0], URIRef('King'))

        # No subject generated
        with self.assertRaises(ResourceWarning):
            subj = sm.resolve(etree.fromstring(XML_STUDENT_2))

        # No subject generated
        with self.assertRaises(ResourceWarning):
            subj = sm.resolve(etree.fromstring(XML_STUDENT_3))

    def test_xml_template(self) -> None:
        """
        Test if we can resolve a template using XML data
        """
        sm = SubjectMap('http://example.com/{/student/id}', ReferenceType.TEMPLATE,
                        MIMEType.TEXT_XML, R2RML.IRI, None)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj[0], URIRef('http://example.com/0'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj[0], URIRef('http://example.com/1'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj[0], URIRef('http://example.com/2'))

    def test_xml_reference(self) -> None:
        """
        Test if we can resolve a reference using XML data
        """
        sm = SubjectMap('/student/name', ReferenceType.REFERENCE,
                        MIMEType.TEXT_XML, R2RML.IRI, None)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj[0], URIRef('Herman'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj[0], URIRef('Ann'))
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj[0], URIRef('Simon'))

    def test_xml_constant(self) -> None:
        """
        Test if we can resolve a constant using XML data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.TEXT_XML, R2RML.IRI, None)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_1))
        self.assertEqual(subj[0], FOAF.Person)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_2))
        self.assertEqual(subj[0], FOAF.Person)
        subj = sm.resolve(etree.fromstring(XML_STUDENT_3))
        self.assertEqual(subj[0], FOAF.Person)

    def test_json_template(self) -> None:
        """
        Test if we can resolve a template using JSON data
        """
        sm = SubjectMap('http://example.com/{$.id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_json_reference(self) -> None:
        """
        Test if we can resolve a reference using JSON data
        """
        sm = SubjectMap('$.name', ReferenceType.REFERENCE,
                        MIMEType.JSON, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_json_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.JSON, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_csv_template(self) -> None:
        """
        Test if we can resolve a template using CSV data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.CSV, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_csv_reference(self) -> None:
        """
        Test if we can resolve a reference using CSV data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.CSV, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_csv_constant(self) -> None:
        """
        Test if we can resolve a constant using CSV data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.CSV, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_tsv_template(self) -> None:
        """
        Test if we can resolve a template using TSV data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.TSV, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_tsv_reference(self) -> None:
        """
        Test if we can resolve a reference using TSV data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.TSV, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_tsv_constant(self) -> None:
        """
        Test if we can resolve a constant using TSV data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.TSV, R2RML.IRI)
        self._check_constant_kv(sm)

    def test_sql_template(self) -> None:
        """
        Test if we can resolve a template using SQL data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.SQL, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_sql_reference(self) -> None:
        """
        Test if we can resolve a reference using SQL data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.SQL, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_sql_constant(self) -> None:
        """
        Test if we can resolve a constant using SQL data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.SQL, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_jsonld_template(self) -> None:
        """
        Test if we can resolve a template using JSON-LD data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON_LD, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_jsonld_reference(self) -> None:
        """
        Test if we can resolve a reference using JSON-LD data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.JSON_LD, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_jsonld_constant(self) -> None:
        """
        Test if we can resolve a constant using JSON-LD data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.JSON_LD, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_n3_template(self) -> None:
        """
        Test if we can resolve a template using N3 data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.N3, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_n3_reference(self) -> None:
        """
        Test if we can resolve a reference using N3 data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.N3, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_n3_constant(self) -> None:
        """
        Test if we can resolve a constant using N3 data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.N3, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_nquads_template(self) -> None:
        """
        Test if we can resolve a template using NQUADS data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.NQUADS, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_nquads_reference(self) -> None:
        """
        Test if we can resolve a reference using NQUADS data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.NQUADS, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_nquads_constant(self) -> None:
        """
        Test if we can resolve a constant using NQUADS data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.NQUADS, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_ntriples_template(self) -> None:
        """
        Test if we can resolve a template using NTRIPLES data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.NTRIPLES, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_ntriples_reference(self) -> None:
        """
        Test if we can resolve a reference using NTRIPLES data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.NTRIPLES, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_ntriples_constant(self) -> None:
        """
        Test if we can resolve a constant using NTRIPLES data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.NTRIPLES, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_rdf_template(self) -> None:
        """
        Test if we can resolve a template using RDF data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.RDF_XML, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_rdf_reference(self) -> None:
        """
        Test if we can resolve a reference using RDF data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.RDF_XML, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_rdf_constant(self) -> None:
        """
        Test if we can resolve a constant using RDF data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.RDF_XML, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_trig_template(self) -> None:
        """
        Test if we can resolve a template using TRIG data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.TRIG, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_trig_reference(self) -> None:
        """
        Test if we can resolve a reference using TRIG data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.TRIG, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_trig_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIG data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.TRIG, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_trix_template(self) -> None:
        """
        Test if we can resolve a template using TRIX data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.TRIX, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_trix_reference(self) -> None:
        """
        Test if we can resolve a reference using TRIX data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                MIMEType.TRIX, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_trix_constant(self) -> None:
        """
        Test if we can resolve a constant using TRIX data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.TRIX, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_turtle_template(self) -> None:
        """
        Test if we can resolve a template using Turtle data
        """
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.TURTLE, R2RML.IRI, None)
        self._check_template_kv(sm)

    def test_turtle_reference(self) -> None:
        """
        Test if we can resolve a reference using turtle data
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.TURTLE, R2RML.IRI, None)
        self._check_reference_kv(sm)

    def test_turtle_constant(self) -> None:
        """
        Test if we can resolve a constant using Turtle data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', ReferenceType.CONSTANT,
                        MIMEType.TURTLE, R2RML.IRI, None)
        self._check_constant_kv(sm)

    def test_blanknode_template(self) -> None:
        """
        Test generation of a blank node using template.
        """
        sm = SubjectMap('blank{id}', ReferenceType.TEMPLATE,
                        MIMEType.TURTLE, R2RML.BlankNode, None)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj[0], BNode('blank0'))

    def test_blanknode_reference(self) -> None:
        """
        Test generation of a blank node using constant.
        """
        sm = SubjectMap('name', ReferenceType.REFERENCE,
                        MIMEType.TURTLE, R2RML.BlankNode, None)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj[0], BNode('Herman'))

    def test_blanknode_constant(self) -> None:
        """
        Test generation of a blank node using constant.
        """
        sm = SubjectMap('myBlankNode', ReferenceType.CONSTANT,
                        MIMEType.TURTLE, R2RML.BlankNode, None)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj[0], BNode('myBlankNode'))


if __name__ == '__main__':
    unittest.main()
