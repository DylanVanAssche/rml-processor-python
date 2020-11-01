#!/usr/bin/env python

import unittest
from rdflib.term import URIRef, Literal
from os import environ
from os.path import abspath

from rml.io.sources import JSONLogicalSource, XMLLogicalSource, \
                           CSVLogicalSource, SPARQLXMLLogicalSource, \
                           SPARQLJSONLogicalSource, SQLLogicalSource, \
                           RDFLogicalSource, DCATLogicalSource, \
                           MIMEType, LogicalSource, CSVWTrimMode
from rml.io.maps import SubjectMap, PredicateMap, ObjectMap, \
                        PredicateObjectMap, TriplesMap, ReferenceType
from rml.namespace import FOAF, LINKED_CONNECTIONS, XSD, R2RML

# Resolve RDF file to absolute path for SPARQL
student_rdf_path = abspath('tests/assets/rdf/student.rdf')
CONJUCTIVE_QUERY = """
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
QUERY = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?person ?name ?age
WHERE {
    ?person foaf:name ?name .
    ?person foaf:age ?age .
}
ORDER BY DESC(?age)
"""
SPARQL_QUERY = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?actor ?name ?birthDate WHERE {
        ?tvshow rdf:type dbo:TelevisionShow .
        ?tvshow rdfs:label 'Friends'@en .
        ?tvshow dbo:starring ?actor .
        ?actor foaf:name ?name .
        ?actor dbo:birthDate ?birthDate .
    }
"""
QUERY_HYDRA = """
PREFIX lc:  <http://semweb.mmlab.be/ns/linkedconnections#>
SELECT ?connection ?departure ?arrival
WHERE {
    ?connection lc:departureStop ?departure .
    ?connection lc:arrivalStop ?arrival .
}
ORDER BY DESC(?connection)
"""
HOST = environ['HOST']


class TriplesMapTests(unittest.TestCase):
    def _assert_single_triple(self, tm: TriplesMap) -> bool:
        # Triple 1
        expected_result = [(URIRef('http://example.com/0'), \
                            FOAF.name, \
                            Literal('Herman'), None)]
        self.assertEqual(next(tm), expected_result)

        # Triple 2
        expected_result = [(URIRef('http://example.com/1'), \
                            FOAF.name, \
                            Literal('Ann'), None)]
        self.assertEqual(next(tm), expected_result)

        # Triple 3
        expected_result = [(URIRef('http://example.com/2'), \
                            FOAF.name, \
                            Literal('Simon'), None)]
        self.assertEqual(next(tm), expected_result)

        with self.assertRaises(StopIteration):
            next(tm)

        return True

    def _assert_multiple_triples(self, tm:TriplesMap) -> bool:
        # Triples 1
        expected_result = [(URIRef('http://example.com/0'), \
                            FOAF.name, \
                            Literal('Herman'), None), \
                           (URIRef('http://example.com/0'), \
                            FOAF.age, \
                            Literal('65'), None)]
        self.assertEqual(next(tm), expected_result)

        # Triples 2
        expected_result = [(URIRef('http://example.com/1'), \
                            FOAF.name, \
                            Literal('Ann'), None),
                           (URIRef('http://example.com/1'), \
                            FOAF.age, \
                            Literal('62'), None)]
        self.assertEqual(next(tm), expected_result)

        # Triples 3
        expected_result = [(URIRef('http://example.com/2'), \
                            FOAF.name, \
                            Literal('Simon'), None),
                           (URIRef('http://example.com/2'), \
                            FOAF.age, \
                            Literal('23'), None)]
        self.assertEqual(next(tm), expected_result)

        with self.assertRaises(StopIteration):
            next(tm)

        return True

    def _assert_sparql_single_triple(self, tm: TriplesMap) -> bool:
        expected_result = [(URIRef('http://dbpedia.org/resource/Jennifer_Aniston'), \
                            FOAF.name, Literal('Jennifer Aniston'), None)]
        self.assertEqual(next(tm), expected_result)
        return True

    def _assert_sparql_multiple_triples(self, tm: TriplesMap) -> bool:
        expected_result = [(URIRef('http://dbpedia.org/resource/Jennifer_Aniston'), \
                            FOAF.name, Literal('Jennifer Aniston'), None), \
                           (URIRef('http://dbpedia.org/resource/Jennifer_Aniston'), \
                            URIRef('http://xmlns.com/foaf/0.1/age'), \
                            Literal('1969-2-11'), None)]
        self.assertEqual(next(tm), expected_result)

        expected_result = [(URIRef('http://dbpedia.org/resource/Jennifer_Aniston'), \
                            FOAF.name, Literal('Jennifer Aniston'), None),
                           (URIRef('http://dbpedia.org/resource/Jennifer_Aniston'), \
                            URIRef('http://xmlns.com/foaf/0.1/age'), \
                            Literal('1969-02-11'), None)]
        self.assertEqual(next(tm), expected_result)

        expected_result = [(URIRef('http://dbpedia.org/resource/David_Schwimmer'), \
                            FOAF.name, Literal('David Schwimmer'), None), \
                           (URIRef('http://dbpedia.org/resource/David_Schwimmer'), \
                            URIRef('http://xmlns.com/foaf/0.1/age'), \
                            Literal('1966-11-2'), None)]
        self.assertEqual(next(tm), expected_result)

        expected_result = [(URIRef('http://dbpedia.org/resource/David_Schwimmer'), \
                            FOAF.name, Literal('David Schwimmer'), None), \
                           (URIRef('http://dbpedia.org/resource/David_Schwimmer'), \
                            URIRef('http://xmlns.com/foaf/0.1/age'), \
                            Literal('1966-11-02'), None)]
        self.assertEqual(next(tm), expected_result)
        return True

    def _build_triples_map_single_triple(self, ls: LogicalSource,
                                         mime_type: MIMEType) -> TriplesMap:
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        mime_type, R2RML.IRI, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          mime_type)
        om = ObjectMap('name', ReferenceType.REFERENCE, mime_type, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        return tm

    def _build_triples_map_single_triple_rdf(self, ls: LogicalSource,
                                             mime_type: MIMEType) -> TriplesMap:
        sm = SubjectMap('{person}', ReferenceType.TEMPLATE,
                        mime_type, R2RML.IRI, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          mime_type)
        om = ObjectMap('name', ReferenceType.REFERENCE, mime_type, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        return tm

    def _build_triples_map_multiple_triples(self, ls: LogicalSource, mime_type:
            MIMEType) -> TriplesMap:
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        mime_type, R2RML.IRI, None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                           mime_type)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                           mime_type)
        om1 = ObjectMap('name', ReferenceType.REFERENCE, mime_type, is_iri=False)
        om2 = ObjectMap('age', ReferenceType.REFERENCE, mime_type, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)
        return tm

    def _build_triples_map_multiple_triples_rdf(self, ls: LogicalSource, \
            mime_type: MIMEType) -> TriplesMap:
        sm = SubjectMap('{person}', ReferenceType.TEMPLATE, mime_type, R2RML.IRI,
                        None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                           mime_type)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                           mime_type)
        om1 = ObjectMap('name', ReferenceType.REFERENCE, mime_type, is_iri=False)
        om2 = ObjectMap('age', ReferenceType.REFERENCE, mime_type, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)
        return tm

    def test_missing_pom_result(self) -> None:
        """
        Test if we can skip PredicateObjectMaps which cannot be resolved
        because the data are missing.
        """
        ls = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, R2RML.IRI, None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om2 = ObjectMap('oops', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)
        self.assertEqual(len(next(tm)), 1)  # Expected: 2 but 'oops' is skipped

    def test_missing_subj_result(self) -> None:
        """
        Test if TriplesMap is ignored when the SubjectMap resolvement fails due
        to missing data.
        """
        ls = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{oops}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, R2RML.IRI, None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om2 = ObjectMap('age', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)
        self.assertEqual(len(next(tm)), 0)  # SubjectMap not resolved

    def test_named_graph(self) -> None:
        """
        Test named graph generation.
        """
        ls = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, R2RML.IRI, None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om2 = ObjectMap('age', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1, \
                rr_graph = URIRef('http://example.com/Graph')))
        pom.append(PredicateObjectMap(pm2, om2, rr_graph = None))
        tm = TriplesMap(ls, sm, pom)
        self.assertEqual(next(tm)[0][3], URIRef('http://example.com/Graph'))
        self.assertEqual(len(next(tm)), 2)

    def test_iterator(self) -> None:
        """
        Test if we can create an iterator from a Triples Map.
        """
        ls = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, R2RML.IRI, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        iterator = iter(tm)

    def test_json_generate_triple(self) -> None:
        """
        Test if we can generate a triple using JSON data.
        """
        ls = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        tm = self._build_triples_map_single_triple(ls, MIMEType.JSON)
        self.assertTrue(self._assert_single_triple(tm))

    def test_json_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using JSON data.
        """
        ls = JSONLogicalSource('$.students.[*]',
                              'tests/assets/json/student.json')
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.JSON)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using XML data.
        """
        ls = XMLLogicalSource('/students/student',
                               'tests/assets/xml/student.xml')
        tm = self._build_triples_map_single_triple(ls, MIMEType.TEXT_XML)
        self.assertTrue(self._assert_single_triple(tm))

    def test_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using XML data.
        """
        ls = XMLLogicalSource('/students/student',
                              'tests/assets/xml/student.xml')
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.TEXT_XML)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_csv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using CSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.csv')
        tm = self._build_triples_map_single_triple(ls, MIMEType.CSV)
        self.assertTrue(self._assert_single_triple(tm))

    def test_csv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using CSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.csv')
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.CSV)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_csv_dialect_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using a CSV dialect as data.
        """
        ls = CSVLogicalSource('tests/assets/csv/dialect_mix.csv',
                              double_quote=True,
                              trim_mode=CSVWTrimMode.START_AND_END,
                              skip_initial_space=True, has_header=True,
                              comment_prefix='$')
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.CSV)
        # Triples 1
        expected_result = [(URIRef('http://example.com/0'), \
                            FOAF.name, \
                            Literal('"Herman"'), None), \
                           (URIRef('http://example.com/0'), \
                            FOAF.age, \
                            Literal('65'), None)]
        self.assertEqual(next(tm), expected_result)

        # Triples 2
        expected_result = [(URIRef('http://example.com/1'), \
                            FOAF.name, \
                            Literal('"Ann"'), None),
                           (URIRef('http://example.com/1'), \
                            FOAF.age, \
                            Literal('62'), None)]
        self.assertEqual(next(tm), expected_result)

        # Triples 3
        expected_result = [(URIRef('http://example.com/2'), \
                            FOAF.name, \
                            Literal('Simon'), None),
                           (URIRef('http://example.com/2'), \
                            FOAF.age, \
                            Literal('23'), None)]
        self.assertEqual(next(tm), expected_result)

        with self.assertRaises(StopIteration):
            next(tm)

    def test_tsv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using TSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.tsv', delimiter='\t')
        tm = self._build_triples_map_single_triple(ls, MIMEType.TSV)
        self.assertTrue(self._assert_single_triple(tm))

    def test_tsv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using TSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.tsv', delimiter='\t')
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.TSV)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_sparql_json_generate_triple(self) -> None:
        """
        Test if we can generate a triple using SPARQL JSON data.
        """
        ls = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                     'http://dbpedia.org/sparql',
                                     SPARQL_QUERY)
        sm = SubjectMap('{actor.value}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, R2RML.IRI, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap('name.value', ReferenceType.REFERENCE, MIMEType.JSON,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        self._assert_sparql_single_triple(tm)

    def test_sparql_json_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using SPARQL JSON data.
        """
        ls = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                     'http://dbpedia.org/sparql',
                                     SPARQL_QUERY)
        sm = SubjectMap('{actor.value}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, R2RML.IRI, None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name.value', ReferenceType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        om2 = ObjectMap('birthDate.value', ReferenceType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)
        self._assert_sparql_multiple_triples(tm)

    def test_sparql_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using SPARQL XML data.
        """
        ls = SPARQLXMLLogicalSource('//sr:result',
                                    'http://dbpedia.org/sparql',
                                    SPARQL_QUERY)
        sm = SubjectMap('{./sr:binding[@name="actor"]/sr:uri}',
                        ReferenceType.TEMPLATE, MIMEType.TEXT_XML, R2RML.IRI, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.TEXT_XML)
        om = ObjectMap('./sr:binding[@name="name"]/sr:literal',
                       ReferenceType.REFERENCE, MIMEType.TEXT_XML, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        self._assert_sparql_single_triple(tm)

    def test_sparql_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using SPARQL XML data.
        """
        ls = SPARQLXMLLogicalSource('//sr:result',
                                    'http://dbpedia.org/sparql',
                                    SPARQL_QUERY)
        sm = SubjectMap('{./sr:binding[@name="actor"]/sr:uri}', ReferenceType.TEMPLATE,
                        MIMEType.TEXT_XML, R2RML.IRI, None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                           MIMEType.TEXT_XML)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                           MIMEType.TEXT_XML)
        om1 = ObjectMap('./sr:binding[@name="name"]/sr:literal',
                        ReferenceType.REFERENCE, MIMEType.TEXT_XML, is_iri=False)
        om2 = ObjectMap('./sr:binding[@name="birthDate"]/sr:literal',
                        ReferenceType.REFERENCE, MIMEType.TEXT_XML, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)
        self._assert_sparql_multiple_triples(tm)

    def test_sql_generate_triple(self) -> None:
        """
        Test if we can generate a triple using SQL data.
        """
        ls = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                              'SELECT id, name, age FROM students;')
        sm = SubjectMap('http://example.com/{ID}', ReferenceType.TEMPLATE,
                        MIMEType.SQL, R2RML.IRI, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.SQL)
        om = ObjectMap('NAME', ReferenceType.REFERENCE, MIMEType.SQL, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        self.assertTrue(self._assert_single_triple(tm))

    def test_sql_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using SQL data.
        """
        ls = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                              'SELECT id, name, age FROM students;')
        sm = SubjectMap('http://example.com/{ID}', ReferenceType.TEMPLATE,
                        MIMEType.SQL, R2RML.IRI, None)
        pm1 = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                           MIMEType.SQL)
        pm2 = PredicateMap('http://xmlns.com/foaf/0.1/age', ReferenceType.CONSTANT,
                           MIMEType.SQL)
        om1 = ObjectMap('NAME', ReferenceType.REFERENCE, MIMEType.SQL,
                        is_iri=False)
        om2 = ObjectMap('AGE', ReferenceType.REFERENCE, MIMEType.SQL,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_rdf_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using RDF XML data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.rdf',
                              QUERY,
                              MIMEType.RDF_XML)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.RDF_XML)
        self.assertTrue(self._assert_single_triple(tm))

    def test_rdf_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using RDF XML data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.rdf',
                              QUERY,
                              MIMEType.RDF_XML)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.RDF_XML)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_jsonld_generate_triple(self) -> None:
        """
        Test if we can generate a triple using JSON-LD data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.jsonld',
                              QUERY,
                              MIMEType.JSON_LD)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.JSON_LD)
        self.assertTrue(self._assert_single_triple(tm))

    def test_jsonld_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using JSON-LD data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.jsonld',
                              QUERY,
                              MIMEType.JSON_LD)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.JSON_LD)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_nquads_generate_triple(self) -> None:
        """
        Test if we can generate a triple using NQUADS data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.nquads',
                              QUERY,
                              MIMEType.NQUADS)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.NQUADS)
        self.assertTrue(self._assert_single_triple(tm))

    def test_nquads_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using NQUADS data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.nquads',
                              QUERY,
                              MIMEType.NQUADS)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.NQUADS)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_trig_generate_triple(self) -> None:
        """
        Test if we can generate a triple using TRIG data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trig',
                              QUERY,
                              MIMEType.TRIG)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.TRIG)
        self.assertTrue(self._assert_single_triple(tm))

    def test_trig_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using TRIG data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trig',
                              QUERY,
                              MIMEType.TRIG)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.TRIG)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_trix_generate_triple(self) -> None:
        """
        Test if we can generate a triple using TRIX data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trix',
                              QUERY,
                              MIMEType.TRIX)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.TRIX)
        self.assertTrue(self._assert_single_triple(tm))

    def test_trix_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using TRIX data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trix',
                              QUERY,
                              MIMEType.TRIX)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.TRIX)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_n3_generate_triple(self) -> None:
        """
        Test if we can generate a triple using N3 data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.n3',
                              QUERY,
                              MIMEType.N3)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.N3)
        self.assertTrue(self._assert_single_triple(tm))

    def test_n3_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using N3 data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.n3',
                              QUERY,
                              MIMEType.N3)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.N3)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_turtle_generate_triple(self) -> None:
        """
        Test if we can generate a triple using Turtle data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ttl',
                              QUERY,
                              MIMEType.TURTLE)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.TURTLE)
        self.assertTrue(self._assert_single_triple(tm))

    def test_turtle_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using Turtle data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ttl',
                              QUERY,
                              MIMEType.TURTLE)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.TURTLE)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_ntriples_generate_triple(self) -> None:
        """
        Test if we can generate a triple using NTRIPLES data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ntriples',
                              QUERY,
                              MIMEType.NTRIPLES)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.NTRIPLES)
        self.assertTrue(self._assert_single_triple(tm))

    def test_ntriples_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using NTRIPLES data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ntriples',
                              QUERY,
                              MIMEType.NTRIPLES)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.NTRIPLES)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_json_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT JSON data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/json/student.json',
                               MIMEType.JSON,
                               rml_iterator='$.students.[*]')
        tm = self._build_triples_map_single_triple(ls, MIMEType.JSON)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_json_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT JSON data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/json/student.json',
                               MIMEType.JSON,
                               rml_iterator='$.students.[*]')
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.JSON)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT XML data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/xml/student.xml',
                               MIMEType.APPLICATION_XML,
                               rml_iterator='/students/student')
        tm = self._build_triples_map_single_triple(ls, MIMEType.APPLICATION_XML)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using XML data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/xml/student.xml',
                               MIMEType.APPLICATION_XML,
                               rml_iterator='/students/student')
        tm = self._build_triples_map_multiple_triples(ls,
                                                      MIMEType.APPLICATION_XML)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_csv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT CSV data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.csv',
                               MIMEType.CSV)
        tm = self._build_triples_map_single_triple(ls, MIMEType.CSV)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_csv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT CSV data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.csv',
                               MIMEType.CSV)
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.CSV)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_tsv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT TSV data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.tsv',
                               MIMEType.TSV, delimiter='\t')
        tm = self._build_triples_map_single_triple(ls, MIMEType.TSV)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_tsv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT TSV data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/csv/student.tsv',
                               MIMEType.TSV, delimiter='\t')
        tm = self._build_triples_map_multiple_triples(ls, MIMEType.TSV)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_rdf_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT RDF XML data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.rdf',
                               MIMEType.RDF_XML,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.RDF_XML)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_rdf_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT RDF XML data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.rdf',
                               MIMEType.RDF_XML,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.RDF_XML)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_jsonld_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT JSON-LD data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.jsonld',
                               MIMEType.JSON_LD,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.JSON_LD)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_jsonld_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT JSON-LD data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.jsonld',
                               MIMEType.JSON_LD,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.JSON_LD)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_nquads_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT NQUADS data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.nquads',
                               MIMEType.NQUADS,
                               rml_iterator=CONJUCTIVE_QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.NQUADS)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_nquads_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT NQUADS data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.nquads',
                               MIMEType.NQUADS,
                               rml_iterator=CONJUCTIVE_QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.NQUADS)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_trig_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT TRIG data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.trig',
                               MIMEType.TRIG,
                               rml_iterator=CONJUCTIVE_QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.TRIG)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_trig_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT TRIG data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.trig',
                               MIMEType.TRIG,
                               rml_iterator=CONJUCTIVE_QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.TRIG)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_trix_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT TRIX data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.trix',
                               MIMEType.TRIX,
                               rml_iterator=CONJUCTIVE_QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.TRIX)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_trix_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT TRIX data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.trix',
                               MIMEType.TRIX,
                               rml_iterator=CONJUCTIVE_QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.TRIX)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_n3_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT N3 data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.n3',
                               MIMEType.N3,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.N3)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_n3_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT N3 data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.n3',
                               MIMEType.N3,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.N3)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_turtle_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT Turtle data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.ttl',
                               MIMEType.TURTLE,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.TURTLE)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_turtle_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT Turtle data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.ttl',
                               MIMEType.TURTLE,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.TURTLE)
        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_ntriples_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT NTRIPLES data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.ntriples',
                               MIMEType.NTRIPLES,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_single_triple_rdf(ls, MIMEType.NTRIPLES)
        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_ntriples_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT NTRIPLES data.
        """
        ls = DCATLogicalSource(f'http://{HOST}:8000/tests/assets/rdf/student.ntriples',
                               MIMEType.NTRIPLES,
                               rml_iterator=QUERY)
        tm = self._build_triples_map_multiple_triples_rdf(ls, MIMEType.NTRIPLES)
        self.assertTrue(self._assert_multiple_triples(tm))

