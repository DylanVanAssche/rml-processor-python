import unittest
from contextlib import redirect_stdout
from io import StringIO
from typing import List
from tempfile import NamedTemporaryFile
from os import remove, chmod, chown
from rdflib import Graph
from rdflib.term import URIRef, Literal
from rdflib.compare import to_isomorphic

from rml.io.targets import FileLogicalTarget
from rml.io.sources import JSONLogicalSource, SPARQLJSONLogicalSource, MIMEType
from rml.io.maps import TriplesMap, SubjectMap, PredicateMap, \
                        ObjectMap, PredicateObjectMap, ReferenceType
from rml.namespace import FOAF

SPARQL_QUERY = """
    SELECT DISTINCT ?actor ?name WHERE {
        ?tvshow rdf:type dbo:TelevisionShow.
        ?tvshow rdfs:label "Friends"@en.
        ?tvshow dbo:starring ?actor.
        ?actor foaf:name ?name
    }
"""


class FileLogicalTargetTests(unittest.TestCase):
    def test_non_existing_path(self) -> None:
        """
        Test if a FileNotFoundError is raised when the path does not exists.
        """
        ls = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, None, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        list_tm = []
        list_tm.append(tm)

        # Create temporary file and write triples to it
        with self.assertRaises(FileNotFoundError):
            non_existing_path = '/this/does/not/exist'
            target = FileLogicalTarget(list_tm, non_existing_path,
                                       MIMEType.NTRIPLES)
            target.write_all()

    def test_write_all_single_triples_map(self) -> None:
        """
        Test writing all triples from a single triples map
        """
        ls = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        list_tm = []
        list_tm.append(tm)

        # Create temporary file and write triples to it
        tmp_file = NamedTemporaryFile(delete=False)
        target = FileLogicalTarget(list_tm, tmp_file.name, MIMEType.NTRIPLES)
        target.write_all()

        # Read the generated triples from file
        output = Graph().parse(tmp_file.name, format=MIMEType.NTRIPLES.value)
        output = to_isomorphic(output)

        # Build the expected graph
        expected_output = Graph()
        expected_output.add((URIRef('http://example.com/0'), FOAF.name,
                             Literal('Herman')))
        expected_output.add((URIRef('http://example.com/1'), FOAF.name,
                             Literal('Ann')))
        expected_output.add((URIRef('http://example.com/2'), FOAF.name,
                             Literal('Simon')))
        expected_output = to_isomorphic(expected_output)

        # Assert and clean up temporary file
        self.assertEqual(output, expected_output)
        remove(tmp_file.name)

    def test_write_single_triples_map(self) -> None:
        """
        Test writing a record of triples from a single triples map
        """
        ls = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                        MIMEType.JSON, None, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        list_tm = []
        list_tm.append(tm)

        # Create temporary file and write triples to it
        tmp_file = NamedTemporaryFile(delete=False)
        target = FileLogicalTarget(list_tm, tmp_file.name, MIMEType.NTRIPLES)
        target.write()

        # Read the generated triples from file
        output = Graph().parse(tmp_file.name, format=MIMEType.NTRIPLES.value)
        output = to_isomorphic(output)

        # Build the expected graph
        expected_output = Graph()
        expected_output.add((URIRef('http://example.com/0'), FOAF.name,
                             Literal('Herman')))
        expected_output = to_isomorphic(expected_output)

        # Assert and clean up temporary file
        self.assertEqual(output, expected_output)
        remove(tmp_file.name)

    def test_write_all_multiple_triples_map(self) -> None:
        """
        Test writing all triples from a multiple triples map
        """
        ls1 = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        ls2 = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                      'http://dbpedia.org/sparql',
                                      SPARQL_QUERY)
        sm1 = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                         MIMEType.JSON, None, None)
        sm2 = SubjectMap('actor.value', ReferenceType.REFERENCE,
                         MIMEType.JSON, None, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        om2 = ObjectMap('name.value', ReferenceType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        pom1 = []
        pom2 = []
        pom1.append(PredicateObjectMap(pm, om1))
        pom2.append(PredicateObjectMap(pm, om2))
        tm1 = TriplesMap(ls1, sm1, pom1)
        tm2 = TriplesMap(ls2, sm2, pom2)
        list_tm = []
        list_tm.append(tm1)
        list_tm.append(tm2)

        # Create temporary file and write triples to it
        tmp_file = NamedTemporaryFile(delete=False)
        target = FileLogicalTarget(list_tm, tmp_file.name, MIMEType.NTRIPLES)
        target.write_all()

        # Read the generated triples from file
        output = Graph().parse(tmp_file.name, format=MIMEType.NTRIPLES.value)
        output = to_isomorphic(output)

        # Build the expected graph
        expected_output = Graph()
        expected_output.add((URIRef('http://dbpedia.org/resource/Lisa_Kudrow'), 
                             FOAF.name, Literal('Lisa Kudrow')))
        expected_output.add((URIRef('http://example.com/0'), FOAF.name,
                             Literal('Herman')))
        expected_output.add((URIRef('http://dbpedia.org/resource/'
                             'David_Schwimmer'), FOAF.name,
                             Literal('David Schwimmer')))
        expected_output.add((URIRef('http://dbpedia.org/resource/'
                             'Courteney_Cox'), FOAF.name,
                             Literal('Courteney Cox')))
        expected_output.add((URIRef('http://example.com/2'), FOAF.name,
                             Literal('Simon')))
        expected_output.add((URIRef('http://dbpedia.org/resource/'
                             'Matt_LeBlanc'), FOAF.name,
                             Literal('Matt LeBlanc')))
        expected_output.add((URIRef('http://dbpedia.org/resource/'
                            'Jennifer_Aniston'), FOAF.name,
                            Literal('Jennifer Aniston')))
        expected_output.add((URIRef('http://dbpedia.org/resource/'
                             'Matthew_Perry'), FOAF.name,
                             Literal('Matthew Perry')))
        expected_output.add((URIRef('http://example.com/1'), FOAF.name,
                             Literal('Ann')))
        expected_output = to_isomorphic(expected_output)

        # Assert and clean up temporary file
        self.assertEqual(output, expected_output)
        remove(tmp_file.name)

    def test_write_multiple_triples_map(self) -> None:
        """
        Test writing a single record of triples from a multiple triples map
        """
        ls1 = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        ls2 = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        sm1 = SubjectMap('http://example.com/{id}', ReferenceType.TEMPLATE,
                         MIMEType.JSON, None, None)
        sm2 = SubjectMap('actor.value', ReferenceType.REFERENCE,
                         MIMEType.JSON, None, None)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', ReferenceType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name', ReferenceType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        om2 = ObjectMap('name.value', ReferenceType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        pom1 = []
        pom2 = []
        pom1.append(PredicateObjectMap(pm, om1))
        pom2.append(PredicateObjectMap(pm, om2))
        tm1 = TriplesMap(ls1, sm1, pom1)
        tm2 = TriplesMap(ls2, sm2, pom2)
        list_tm = []
        list_tm.append(tm1)
        list_tm.append(tm2)

        # Create temporary file and write triples to it
        tmp_file = NamedTemporaryFile(delete=False)
        target = FileLogicalTarget(list_tm, tmp_file.name,
                                   MIMEType.NTRIPLES)
        target.write()

        # Read the generated triples from file
        output = Graph().parse(tmp_file.name, format=MIMEType.NTRIPLES.value)
        output = to_isomorphic(output)

        # Build the expected graph
        expected_output = Graph()
        expected_output.add((URIRef('http://example.com/0'), FOAF.name,
                             Literal('Herman')))
        expected_output.add((URIRef('http://dbpedia.org/resource/'
                            'Jennifer_Aniston'), FOAF.name,
                            Literal('Jennifer Aniston')))
        expected_output = to_isomorphic(expected_output)

        # Assert and clean up temporary file
        self.assertEqual(output, expected_output)
        remove(tmp_file.name)


if __name__ == '__main__':
    unittest.main()
