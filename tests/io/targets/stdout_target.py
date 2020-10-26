import unittest
from contextlib import redirect_stdout
from io import StringIO
from typing import List
from rdflib.term import URIRef

from rml.namespace import R2RML, FOAF
from rml.io.targets import StdoutLogicalTarget
from rml.io.sources import JSONLogicalSource, SPARQLJSONLogicalSource, MIMEType
from rml.io.maps import TriplesMap, SubjectMap, PredicateMap, \
                        ObjectMap, PredicateObjectMap, ReferenceType

SPARQL_QUERY = """
    SELECT DISTINCT ?actor ?name WHERE {
        ?tvshow rdf:type dbo:TelevisionShow.
        ?tvshow rdfs:label "Friends"@en.
        ?tvshow dbo:starring ?actor.
        ?actor foaf:name ?name
    }
"""

EXPECTED_OUTPUT_1 = """<http://example.com/0> <http://xmlns.com/foaf/0.1/name> <Herman> .
<http://example.com/1> <http://xmlns.com/foaf/0.1/name> <Ann> .
<http://example.com/2> <http://xmlns.com/foaf/0.1/name> <Simon> .
"""

EXPECTED_OUTPUT_2 = """<http://example.com/0> <http://xmlns.com/foaf/0.1/name> <Herman> .
"""

EXPECTED_OUTPUT_3 = """<http://example.com/0> <http://xmlns.com/foaf/0.1/name> <Herman> .
<http://dbpedia.org/resource/Jennifer_Aniston> <http://xmlns.com/foaf/0.1/name> <Jennifer Aniston> .
<http://example.com/1> <http://xmlns.com/foaf/0.1/name> <Ann> .
<http://dbpedia.org/resource/David_Schwimmer> <http://xmlns.com/foaf/0.1/name> <David Schwimmer> .
<http://example.com/2> <http://xmlns.com/foaf/0.1/name> <Simon> .
<http://dbpedia.org/resource/Lisa_Kudrow> <http://xmlns.com/foaf/0.1/name> <Lisa Kudrow> .
<http://dbpedia.org/resource/Matt_LeBlanc> <http://xmlns.com/foaf/0.1/name> <Matt LeBlanc> .
<http://dbpedia.org/resource/Matthew_Perry> <http://xmlns.com/foaf/0.1/name> <Matthew Perry> .
<http://dbpedia.org/resource/Courteney_Cox> <http://xmlns.com/foaf/0.1/name> <Courteney Cox> .
"""

EXPECTED_OUTPUT_4 = """<http://example.com/0> <http://xmlns.com/foaf/0.1/name> <Herman> .
<http://dbpedia.org/resource/Jennifer_Aniston> <http://xmlns.com/foaf/0.1/name> <Jennifer Aniston> .
"""

EXPECTED_OUTPUT_5 = """
"""


class StdoutLogicalTargetTests(unittest.TestCase):
    def test_write_all_single_triples_map(self) -> None:
        """
        Test write all triples of single triples map
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

        with StringIO() as buf:
            with redirect_stdout(buf):
                target = StdoutLogicalTarget(list_tm)
                target.write_all()
            self.assertEqual(buf.getvalue(), EXPECTED_OUTPUT_1)

    def test_write_single_triples_map(self) -> None:
        """
        Test write a single record of triples of single triples map
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

        with StringIO() as buf:
            with redirect_stdout(buf):
                target = StdoutLogicalTarget(list_tm)
                target.write()
            output = buf.getvalue()
            self.assertEqual(output, EXPECTED_OUTPUT_2)

    def test_write_all_multiple_triples_map(self) -> None:
        """
        Test write all triples of multiple triples maps
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

        with StringIO() as buf:
            with redirect_stdout(buf):
                target = StdoutLogicalTarget(list_tm)
                target.write_all()
            output = buf.getvalue()
            self.assertEqual(output, EXPECTED_OUTPUT_3)

    def test_write_multiple_triples_map(self) -> None:
        """
        Test write a single record of triples of multiple triples maps
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

        with StringIO() as buf:
            with redirect_stdout(buf):
                target = StdoutLogicalTarget(list_tm)
                target.write()
            output = buf.getvalue()
            self.assertEqual(output, EXPECTED_OUTPUT_4)


if __name__ == '__main__':
    unittest.main()
