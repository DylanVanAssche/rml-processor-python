#!/usr/bin/env python

import unittest
from rdflib.term import URIRef, Literal
from os.path import abspath

from rml.io.sources import JSONLogicalSource, XMLLogicalSource, \
                           CSVLogicalSource, SPARQLXMLLogicalSource, \
                           SPARQLJSONLogicalSource, SQLLogicalSource, \
                           RDFLogicalSource, DCATLogicalSource, \
                           HydraLogicalSource, MIMEType
from rml.io.maps import SubjectMap, PredicateMap, ObjectMap, \
                        PredicateObjectMap, TriplesMap, TermType
from rml.namespace import FOAF, LINKED_CONNECTIONS, XSD

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

SPARQL_QUERY = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?actor ?name ?birthDate WHERE {
        ?tvshow rdf:type dbo:TelevisionShow .
        ?tvshow rdfs:label "Friends"@en .
        ?tvshow dbo:starring ?actor .
        ?actor foaf:name ?name .
        ?actor dbo:birthDate ?birthDate .
    }
"""

QUERY_HYDRA="""
PREFIX lc:  <http://semweb.mmlab.be/ns/linkedconnections#>
SELECT ?connection ?departure ?arrival
WHERE {
    ?connection lc:departureStop ?departure .
    ?connection lc:arrivalStop ?arrival .
}
ORDER BY DESC(?connection)
"""

class TriplesMapTests(unittest.TestCase):
    def _assert_single_triple(self, tm: TriplesMap) -> bool:
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

        return True

    def _assert_multiple_triples(self, tm:TriplesMap) -> bool:
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

        return True

    def _assert_hydra_single_triple(self, tm: TriplesMap) -> bool:
        # Hydra page 0
        expected_result = [(URIRef('http://irail.be/connections/8883808/20200619/IC1717'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008883808'))]
        self.assertEqual(next(tm), expected_result)
        expected_result = [(URIRef('http://irail.be/connections/8814159/20200619/IC2039'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008814159'))]
        self.assertEqual(next(tm), expected_result)

        # Hydra page 1
        expected_result = [(URIRef('http://irail.be/connections/8895430/20200619/P8903'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008895430'))]
        self.assertEqual(next(tm), expected_result)
        expected_result = [(URIRef('http://irail.be/connections/8813003/20200619/IC2118'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008813003'))]
        self.assertEqual(next(tm), expected_result)

        # Hydra page 2
        expected_result = [(URIRef('http://irail.be/connections/8833274/20200619/IC2640'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008833274'))]
        self.assertEqual(next(tm), expected_result)
        expected_result = [(URIRef('http://irail.be/connections/8811262/20200619/IC2240'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008811262'))]
        self.assertEqual(next(tm), expected_result)

        return True

    def _assert_hydra_multiple_triples(self, tm:TriplesMap) -> bool:
        # Hydra page 0
        expected_result = [(URIRef('http://irail.be/connections/8883808/20200619/IC1717'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008883808')), \
                            (URIRef('http://irail.be/connections/8883808/20200619/IC1717'), \
                            LINKED_CONNECTIONS.arrivalStop, \
                            URIRef('http://irail.be/stations/NMBS/008814332'))]
        self.assertEqual(next(tm), expected_result)
        expected_result = [(URIRef('http://irail.be/connections/8814159/20200619/IC2039'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008814159')), \
                            (URIRef('http://irail.be/connections/8814159/20200619/IC2039'), \
                            LINKED_CONNECTIONS.arrivalStop, \
                            URIRef('http://irail.be/stations/NMBS/008814167'))]
        self.assertEqual(next(tm), expected_result)

        # Hydra page 1
        expected_result = [(URIRef('http://irail.be/connections/8895430/20200619/P8903'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008895430')), \
                            (URIRef('http://irail.be/connections/8895430/20200619/P8903'), \
                            LINKED_CONNECTIONS.arrivalStop, \
                            URIRef('http://irail.be/stations/NMBS/008895422'))]
        self.assertEqual(next(tm), expected_result)
        expected_result = [(URIRef('http://irail.be/connections/8813003/20200619/IC2118'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008813003')), \
                            (URIRef('http://irail.be/connections/8813003/20200619/IC2118'), \
                            LINKED_CONNECTIONS.arrivalStop, \
                            URIRef('http://irail.be/stations/NMBS/008813045'))]
        self.assertEqual(next(tm), expected_result)

        # Hydra page 2
        expected_result = [(URIRef('http://irail.be/connections/8833274/20200619/IC2640'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008833274')), \
                            (URIRef('http://irail.be/connections/8833274/20200619/IC2640'), \
                            LINKED_CONNECTIONS.arrivalStop, \
                            URIRef('http://irail.be/stations/NMBS/008833266'))]
        self.assertEqual(next(tm), expected_result)
        expected_result = [(URIRef('http://irail.be/connections/8811262/20200619/IC2240'), \
                            LINKED_CONNECTIONS.departureStop, \
                            URIRef('http://irail.be/stations/NMBS/008811262')), \
                            (URIRef('http://irail.be/connections/8811262/20200619/IC2240'), \
                            LINKED_CONNECTIONS.arrivalStop, \
                            URIRef('http://irail.be/stations/NMBS/008811254'))]
        self.assertEqual(next(tm), expected_result)

        return True

    def test_iterator(self) -> None:
        """
        Test if we can create an iterator from a Triples Map.
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
        iterator = iter(tm)

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

        self.assertTrue(self._assert_single_triple(tm))

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

        self.assertTrue(self._assert_multiple_triples(tm))

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

        self.assertTrue(self._assert_single_triple(tm))

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

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_csv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using CSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.csv')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.CSV)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.CSV)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.CSV,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_csv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using CSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.csv')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.CSV)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.CSV)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.CSV)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.CSV,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.CSV,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_tsv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using TSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.tsv', delimiter='\t')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.TSV)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TSV)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TSV,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_tsv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using TSV data.
        """
        ls = CSVLogicalSource('tests/assets/csv/student.tsv', delimiter='\t')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.TSV)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TSV)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TSV)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.TSV,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.TSV,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_sparql_json_generate_triple(self) -> None:
        """
        Test if we can generate a triple using SPARQL JSON data.
        """
        ls = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        sm = SubjectMap("{actor.value}", TermType.TEMPLATE,
                        MIMEType.JSON)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        print(next(tm))

    def test_sparql_json_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using SPARQL JSON data.
        """
        ls = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        sm = SubjectMap("{actor.value}", TermType.TEMPLATE,
                        MIMEType.JSON)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        om2 = ObjectMap("birthDate", TermType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        print(next(tm))

    def test_sparql_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using SPARQL XML data.
        """
        ls = SPARQLXMLLogicalSource('//result',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        sm = SubjectMap('{./binding[@name="actor"]}', TermType.TEMPLATE,
                        MIMEType.TEXT_XML)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TEXT_XML)
        om = ObjectMap('./binding[@name="name"]', TermType.REFERENCE, MIMEType.TEXT_XML,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        print(next(tm))

    def test_sparql_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using SPARQL XML data.
        """
        ls = SPARQLXMLLogicalSource('//result',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        sm = SubjectMap('{./binding[@name="actor"]}', TermType.TEMPLATE,
                        MIMEType.TEXT_XML)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TEXT_XML)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TEXT_XML)
        om1 = ObjectMap('./binding[@name="name"]', TermType.REFERENCE, MIMEType.TEXT_XML,
                        is_iri=False)
        om2 = ObjectMap('./binding[@name="birthDate"]', TermType.REFERENCE, MIMEType.TEXT_XML,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        print(next(tm))

    def test_sql_generate_triple(self) -> None:
        """
        Test if we can generate a triple using SQL data.
        """
        ls = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                                       'SELECT id, name, age FROM students;')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.SQL)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.SQL)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.SQL,
                       is_iri=False)
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
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.SQL)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.SQL)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.SQL)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.SQL,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.SQL,
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
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.SQL)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.SQL)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.RDF_XML,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_rdf_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using RDF XML data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.rdf',
                                       QUERY,
                                       MIMEType.RDF_XML)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.RDF_XML)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.RDF_XML)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.RDF_XML)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.RDF_XML,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.RDF_XML,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_jsonld_generate_triple(self) -> None:
        """
        Test if we can generate a triple using JSON-LD data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.jsonld',
                                       QUERY,
                                       MIMEType.JSON_LD)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.JSON_LD)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON_LD)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON_LD,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_jsonld_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using JSON-LD data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.jsonld',
                                       QUERY,
                                       MIMEType.JSON_LD)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.JSON_LD)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON_LD)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.JSON_LD)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON_LD,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.JSON_LD,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_nquads_generate_triple(self) -> None:
        """
        Test if we can generate a triple using NQUADS data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.nquads',
                                       QUERY,
                                       MIMEType.NQUADS)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NQUADS)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NQUADS)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.NQUADS,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_nquads_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using NQUADS data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.nquads',
                                       QUERY,
                                       MIMEType.NQUADS)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NQUADS)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NQUADS)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.NQUADS)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.NQUADS,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.NQUADS,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_trig_generate_triple(self) -> None:
        """
        Test if we can generate a triple using TRIG data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trig',
                                       QUERY,
                                       MIMEType.TRIG)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIG)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIG)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIG,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_trig_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using TRIG data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trig',
                                       QUERY,
                                       MIMEType.TRIG)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIG)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIG)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TRIG)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIG,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.TRIG,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_trix_generate_triple(self) -> None:
        """
        Test if we can generate a triple using TRIX data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trix',
                                       QUERY,
                                       MIMEType.TRIX)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIX)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIX)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIX,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_trix_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using TRIX data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.trix',
                                       QUERY,
                                       MIMEType.TRIX)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIX)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIX)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TRIX)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIX,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.TRIX,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_n3_generate_triple(self) -> None:
        """
        Test if we can generate a triple using N3 data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.n3',
                                       QUERY,
                                       MIMEType.N3)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.N3)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.N3)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.N3,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_n3_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using N3 data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.n3',
                                       QUERY,
                                       MIMEType.N3)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.N3)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.N3)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.N3)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.N3,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.N3,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_turtle_generate_triple(self) -> None:
        """
        Test if we can generate a triple using Turtle data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ttl',
                                       QUERY,
                                       MIMEType.TURTLE)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TURTLE)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TURTLE)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TURTLE,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_turtle_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using Turtle data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ttl',
                                       QUERY,
                                       MIMEType.TURTLE)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TURTLE)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TURTLE)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TURTLE)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.TURTLE,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.TURTLE,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_ntriples_generate_triple(self) -> None:
        """
        Test if we can generate a triple using NTRIPLES data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ntriples',
                                       QUERY,
                                       MIMEType.NTRIPLES)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NTRIPLES)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NTRIPLES)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.NTRIPLES,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_ntriples_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using NTRIPLES data.
        """
        ls = RDFLogicalSource('tests/assets/rdf/student.ntriples',
                                       QUERY,
                                       MIMEType.NTRIPLES)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NTRIPLES)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NTRIPLES)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.NTRIPLES)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.NTRIPLES,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.NTRIPLES,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_json_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT JSON data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/json/student.json',
                                        MIMEType.JSON,
                                        reference_formulation='$.students.[*]')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.JSON)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_json_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT JSON data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/json/student.json',
                                        MIMEType.JSON,
                                        reference_formulation='$.students.[*]')
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

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT XML data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/xml/student.xml',
                                        MIMEType.APPLICATION_XML,
                                        reference_formulation='/students/student')
        sm = SubjectMap("http://example.com/{./id}", TermType.TEMPLATE,
                        MIMEType.TEXT_XML)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TEXT_XML)
        om = ObjectMap("./name", TermType.REFERENCE, MIMEType.TEXT_XML,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using XML data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/xml/student.xml',
                                        MIMEType.APPLICATION_XML,
                                        reference_formulation='/students/student')
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

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_csv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT CSV data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/student.csv',
                                        MIMEType.CSV)
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.CSV)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.CSV)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.CSV,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_csv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT CSV data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/student.csv',
                                        MIMEType.CSV)
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.CSV)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.CSV)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.CSV)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.CSV,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.CSV,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_tsv_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT TSV data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/student.tsv',
                                        MIMEType.TSV, delimiter='\t')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.TSV)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TSV)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TSV,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_tsv_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT TSV data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/csv/student.tsv',
                                        MIMEType.TSV, delimiter='\t')
        sm = SubjectMap("http://example.com/{id}", TermType.TEMPLATE,
                        MIMEType.CSV)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.CSV)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.CSV)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.CSV,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.CSV,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_rdf_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT RDF XML data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.rdf',
                                        MIMEType.RDF_XML,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.SQL)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.SQL)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.RDF_XML,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_rdf_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT RDF XML data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.rdf',
                                        MIMEType.RDF_XML,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.RDF_XML)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.RDF_XML)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.RDF_XML)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.RDF_XML,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.RDF_XML,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_jsonld_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT JSON-LD data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.jsonld',
                                        MIMEType.JSON_LD,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.JSON_LD)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON_LD)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON_LD,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_jsonld_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT JSON-LD data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.jsonld',
                                        MIMEType.JSON_LD,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.JSON_LD)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.JSON_LD)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.JSON_LD)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.JSON_LD,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.JSON_LD,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_nquads_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT NQUADS data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.nquads',
                                        MIMEType.NQUADS,
                                        reference_formulation=CONJUCTIVE_QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NQUADS)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NQUADS)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.NQUADS,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_nquads_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT NQUADS data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.nquads',
                                        MIMEType.NQUADS,
                                        reference_formulation=CONJUCTIVE_QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NQUADS)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NQUADS)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.NQUADS)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.NQUADS,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.NQUADS,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_trig_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT TRIG data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.trig',
                                        MIMEType.TRIG,
                                        reference_formulation=CONJUCTIVE_QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIG)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIG)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIG,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_trig_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT TRIG data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.trig',
                                        MIMEType.TRIG,
                                        reference_formulation=CONJUCTIVE_QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIG)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIG)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TRIG)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIG,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.TRIG,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_trix_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT TRIX data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.trix',
                                        MIMEType.TRIX,
                                        reference_formulation=CONJUCTIVE_QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIX)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIX)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIX,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_trix_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT TRIX data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.trix',
                                        MIMEType.TRIX,
                                        reference_formulation=CONJUCTIVE_QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TRIX)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TRIX)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TRIX)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.TRIX,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.TRIX,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_n3_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT N3 data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.n3',
                                        MIMEType.N3,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.N3)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.N3)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.N3,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_n3_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT N3 data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.n3',
                                        MIMEType.N3,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.N3)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.N3)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.N3)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.N3,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.N3,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_turtle_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT Turtle data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.ttl',
                                        MIMEType.TURTLE,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TURTLE)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TURTLE)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.TURTLE,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_turtle_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT Turtle data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.ttl',
                                        MIMEType.TURTLE,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.TURTLE)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.TURTLE)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.TURTLE)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.TURTLE,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.TURTLE,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_dcat_ntriples_generate_triple(self) -> None:
        """
        Test if we can generate a triple using DCAT NTRIPLES data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.ntriples',
                                        MIMEType.NTRIPLES,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NTRIPLES)
        pm = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NTRIPLES)
        om = ObjectMap("name", TermType.REFERENCE, MIMEType.NTRIPLES,
                       is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_single_triple(tm))

    def test_dcat_ntriples_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using DCAT NTRIPLES data.
        """
        ls = DCATLogicalSource('http://127.0.0.1:8000/tests/assets/rdf/student.ntriples',
                                        MIMEType.NTRIPLES,
                                        reference_formulation=QUERY)
        sm = SubjectMap("{person}", TermType.TEMPLATE,
                        MIMEType.NTRIPLES)
        pm1 = PredicateMap("http://xmlns.com/foaf/0.1/name", TermType.CONSTANT,
                          MIMEType.NTRIPLES)
        pm2 = PredicateMap("http://xmlns.com/foaf/0.1/age", TermType.CONSTANT,
                          MIMEType.NTRIPLES)
        om1 = ObjectMap("name", TermType.REFERENCE, MIMEType.NTRIPLES,
                        is_iri=False)
        om2 = ObjectMap("age", TermType.REFERENCE, MIMEType.NTRIPLES,
                        is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_multiple_triples(tm))

    def test_hydra_jsonld_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA JSON-LD data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.jsonld',
                                    MIMEType.JSON_LD,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.JSON_LD)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.JSON_LD)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.JSON_LD)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_jsonld_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA JSON-LD data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.jsonld',
                                    MIMEType.JSON_LD,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.JSON_LD)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.JSON_LD)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                          TermType.CONSTANT, MIMEType.JSON_LD)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.JSON_LD)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.JSON_LD)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))

    def test_hydra_rdf_xml_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA RDF XML data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.rdf',
                                    MIMEType.RDF_XML,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.SQL)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.SQL)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.RDF_XML)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_rdf_xml_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA RDF XML data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.rdf',
                                    MIMEType.RDF_XML,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.RDF_XML)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                           TermType.CONSTANT, MIMEType.RDF_XML)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                           TermType.CONSTANT, MIMEType.RDF_XML)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.RDF_XML)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.RDF_XML)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))

    def test_hydra_turtle_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA Turtle data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.ttl',
                                    MIMEType.TURTLE,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.TURTLE)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.TURTLE)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.TURTLE)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_turtle_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA Turtle data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.ttl',
                                    MIMEType.TURTLE,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.TURTLE)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                           TermType.CONSTANT, MIMEType.TURTLE)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                           TermType.CONSTANT, MIMEType.TURTLE)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.TURTLE)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.TURTLE)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))

    def test_hydra_ntriples_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA NTRIPLES data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.ntriples',
                                    MIMEType.NTRIPLES,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.NTRIPLES)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.NTRIPLES)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.NTRIPLES)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_ntriples_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA NTRIPLES data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.ntriples',
                                    MIMEType.NTRIPLES,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.NTRIPLES)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                           TermType.CONSTANT, MIMEType.NTRIPLES)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                           TermType.CONSTANT, MIMEType.NTRIPLES)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.NTRIPLES)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.NTRIPLES)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))

    def test_hydra_nquads_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA NQUADS data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.nquads',
                                    MIMEType.NQUADS,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.NQUADS)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.NQUADS)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.NQUADS)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_nquads_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA NQUADS data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.nquads',
                                    MIMEType.NQUADS,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.NQUADS)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.NQUADS)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                          TermType.CONSTANT, MIMEType.NQUADS)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.NQUADS)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.NQUADS)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))

    def test_hydra_trig_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA TRIG data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.trig',
                                    MIMEType.TRIG,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.TRIG)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.TRIG)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.TRIG)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_trig_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA TRIG data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.trig',
                                    MIMEType.TRIG,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.TRIG)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                           TermType.CONSTANT, MIMEType.TRIG)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                           TermType.CONSTANT, MIMEType.TRIG)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.TRIG)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.TRIG)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))

    def test_hydra_trix_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA TRIX data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.trix',
                                    MIMEType.TRIX,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.TRIX)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.TRIX)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.TRIX)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_trix_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA TRIX data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.trix',
                                    MIMEType.TRIX,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.TRIX)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                           TermType.CONSTANT, MIMEType.TRIX)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                           TermType.CONSTANT, MIMEType.TRIX)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.TRIX)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.TRIX)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))

    def test_hydra_n3_generate_triple(self) -> None:
        """
        Test if we can generate a triple using HYDRA N3 data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.n3',
                                    MIMEType.N3,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.N3)
        pm = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                          TermType.CONSTANT, MIMEType.N3)
        om = ObjectMap("departure", TermType.REFERENCE, MIMEType.N3)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_single_triple(tm))

    def test_hydra_n3_generate_multiple_triples(self) -> None:
        """
        Test if we can generate multiple triples using HYDRA N3 data.
        """
        ls = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.n3',
                                    MIMEType.N3,
                                    reference_formulation=QUERY_HYDRA)
        sm = SubjectMap("{connection}", TermType.TEMPLATE,
                        MIMEType.N3)
        pm1 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#departureStop",
                           TermType.CONSTANT, MIMEType.N3)
        pm2 = PredicateMap("http://semweb.mmlab.be/ns/linkedconnections#arrivalStop",
                           TermType.CONSTANT, MIMEType.N3)
        om1 = ObjectMap("departure", TermType.REFERENCE, MIMEType.N3)
        om2 = ObjectMap("arrival", TermType.REFERENCE, MIMEType.N3)
        pom = []
        pom.append(PredicateObjectMap(pm1, om1))
        pom.append(PredicateObjectMap(pm2, om2))
        tm = TriplesMap(ls, sm, pom)

        self.assertTrue(self._assert_hydra_multiple_triples(tm))
