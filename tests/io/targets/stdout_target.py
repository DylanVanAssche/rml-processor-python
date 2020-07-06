import unittest
from contextlib import redirect_stdout
from io import StringIO
from typing import List

from rml.io.targets import StdoutLogicalTarget
from rml.io.sources import JSONLogicalSource, SPARQLJSONLogicalSource, MIMEType
from rml.io.maps import TriplesMap, SubjectMap, PredicateMap, \
                        ObjectMap, PredicateObjectMap, TermType

SPARQL_QUERY = """
    SELECT DISTINCT ?actor ?name WHERE {
        ?tvshow rdf:type dbo:TelevisionShow.
        ?tvshow rdfs:label "Friends"@en.
        ?tvshow dbo:starring ?actor.
        ?actor foaf:name ?name
    }
"""


class StdoutLogicalTargetTests(unittest.TestCase):
    def test_write_all_single_triples_map(self) -> None:
        """
        Test write all triples of single triples map
        """
        ls = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.JSON)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', TermType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap('name', TermType.REFERENCE, MIMEType.JSON, is_iri=False)
        pom = []
        pom.append(PredicateObjectMap(pm, om))
        tm = TriplesMap(ls, sm, pom)
        list_tm = []
        list_tm.append(tm)

        with StringIO() as buf:
            with redirect_stdout(buf):
                target = StdoutLogicalTarget(list_tm)
                target.write_all()
            self.assertEqual(buf.getvalue(),
                             '<http://example.com/0> '
                             '<http://xmlns.com/foaf/0.1/name> <Herman>\n'
                             '<http://example.com/1> '
                             '<http://xmlns.com/foaf/0.1/name> <Ann>\n'
                             '<http://example.com/2> '
                             '<http://xmlns.com/foaf/0.1/name> <Simon>\n')

    def test_write_single_triples_map(self) -> None:
        """
        Test write a single record of triples of single triples map
        """
        ls = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        sm = SubjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.JSON)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', TermType.CONSTANT,
                          MIMEType.JSON)
        om = ObjectMap('name', TermType.REFERENCE, MIMEType.JSON, is_iri=False)
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
            self.assertEqual(output,
                             '<http://example.com/0> '
                             '<http://xmlns.com/foaf/0.1/name> <Herman>\n')

    def test_write_all_multiple_triples_map(self) -> None:
        """
        Test write all triples of multiple triples maps
        """
        ls1 = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        ls2 = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        sm1 = SubjectMap('http://example.com/{id}', TermType.TEMPLATE,
                         MIMEType.JSON)
        sm2 = SubjectMap('actor.value', TermType.REFERENCE,
                         MIMEType.JSON)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', TermType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name', TermType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        om2 = ObjectMap('name.value', TermType.REFERENCE, MIMEType.JSON,
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
            self.assertEqual(output,
                             '<http://example.com/0> '
                             '<http://xmlns.com/foaf/0.1/name> <Herman>\n'
                             '<http://dbpedia.org/resource/Jennifer_Aniston> '
                             '<http://xmlns.com/foaf/0.1/name> '
                             '<Jennifer Aniston>\n'
                             '<http://example.com/1> '
                             '<http://xmlns.com/foaf/0.1/name> <Ann>\n'
                             '<http://dbpedia.org/resource/David_Schwimmer> '
                             '<http://xmlns.com/foaf/0.1/name> '
                             '<David Schwimmer>\n'
                             '<http://example.com/2> '
                             '<http://xmlns.com/foaf/0.1/name> <Simon>\n'
                             '<http://dbpedia.org/resource/Lisa_Kudrow> '
                             '<http://xmlns.com/foaf/0.1/name> <Lisa Kudrow>\n'
                             '<http://dbpedia.org/resource/Matt_LeBlanc> '
                             '<http://xmlns.com/foaf/0.1/name> '
                             '<Matt LeBlanc>\n'
                             '<http://dbpedia.org/resource/Matthew_Perry> '
                             '<http://xmlns.com/foaf/0.1/name> '
                             '<Matthew Perry>\n'
                             '<http://dbpedia.org/resource/Courteney_Cox> '
                             '<http://xmlns.com/foaf/0.1/name> '
                             '<Courteney Cox>\n')

    def test_write_multiple_triples_map(self) -> None:
        """
        Test write a single record of triples of multiple triples maps
        """
        ls1 = JSONLogicalSource('$.students.[*]',
                               'tests/assets/json/student.json')
        ls2 = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        sm1 = SubjectMap('http://example.com/{id}', TermType.TEMPLATE,
                         MIMEType.JSON)
        sm2 = SubjectMap('actor.value', TermType.REFERENCE,
                         MIMEType.JSON)
        pm = PredicateMap('http://xmlns.com/foaf/0.1/name', TermType.CONSTANT,
                          MIMEType.JSON)
        om1 = ObjectMap('name', TermType.REFERENCE, MIMEType.JSON,
                        is_iri=False)
        om2 = ObjectMap('name.value', TermType.REFERENCE, MIMEType.JSON,
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
            self.assertEqual(output,
                             '<http://example.com/0> '
                             '<http://xmlns.com/foaf/0.1/name> <Herman>\n'
                             '<http://dbpedia.org/resource/Jennifer_Aniston> '
                             '<http://xmlns.com/foaf/0.1/name> '
                             '<Jennifer Aniston>\n')


if __name__ == '__main__':
    unittest.main()
