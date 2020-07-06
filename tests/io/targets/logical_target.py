import unittest
from typing import List, Tuple
from rdflib.term import URIRef, Identifier

from rml.io.targets import LogicalTarget
from rml.io.sources import JSONLogicalSource, MIMEType
from rml.io.maps import TriplesMap, SubjectMap, PredicateMap, \
                        ObjectMap, PredicateObjectMap, TermType


class MockLogicalTarget(LogicalTarget):
    def __init__(self, triples_maps: List[TriplesMap]) -> None:
        super().__init__(triples_maps)

    def _add_to_target(self,
                       triple: Tuple[URIRef, URIRef, Identifier]) -> None:
        print(triple)


class LogicalTargetTests(unittest.TestCase):
    def test_has_methods_and_attributes(self) -> None:
        """
        Test Logical Target methods and attributes
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

        mock = MockLogicalTarget(list_tm)
        self.assertTrue(hasattr(mock, '_triples_maps'))
        self.assertTrue(hasattr(mock, '_number_of_triples_maps'))
        self.assertTrue(callable(mock.write))
        self.assertTrue(callable(mock.write_all))


if __name__ == '__main__':
    unittest.main()
