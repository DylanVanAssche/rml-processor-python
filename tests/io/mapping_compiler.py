import unittest
from os import environ
from typing import List, Tuple
from rdflib import Graph
from rdflib.term import Literal
from rdflib.compare import to_isomorphic
from tempfile import NamedTemporaryFile

from rml.io.mapping_compiler import MappingCompiler
from rml.io.maps import TriplesMap
from rml.namespace import D2RQ, RML, R2RML

from rdflib.plugins.serializers.turtle import TurtleSerializer


class MappingCompilerTests(unittest.TestCase):
    def _compile_rules(self, path1: str, path2: str) -> Tuple[Graph, Graph]:
        m = MappingCompiler()
        g1 = m.compile(Graph().parse(path1, format='turtle'))
        g1 = to_isomorphic(g1)
        g2 = Graph().parse(path2, format='turtle')
        g2 = to_isomorphic(g2)
        return g1, g2

    def test_expand_shortcuts(self) -> None:
        """
        Test shortcut expansion of rr:subject, rr:object, rr:predicate and
        rr:graph.
        """
        p1 = 'tests/assets/io/mapping_files/mapping_shortcuts.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_shortcuts_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        self.assertEqual(g1, g2, 'Shortcuts not correctly expanded!')

    def test_strip_jdbc(self) -> None:
        """
        Test stripping 'jdbc' part of the JDBC string for databases.
        """
        p = 'tests/assets/io/mapping_files/mapping_sql.ttl'
        m = MappingCompiler()
        g1 = m.compile(Graph().parse(p, format='turtle'))

        # Check if jdbc: is stripped
        for t in g1.triples((None, D2RQ.jdbcDSN, None)):
            self.assertFalse('jdbc:' in str(t[2]))

    def test_rewrite_rr_table_name(self) -> None:
        """
        Test rewriting rr:tableName into rml:query
        """
        p1 = 'tests/assets/io/mapping_files/mapping_rr_table_name.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_rr_table_name_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        for tm in g1.triples((None, R2RML.TriplesMap, None)):
            ls = g1.value(tm, RML.logicalSource)
            self.assertIsNotNone(g1.value(ls, RML.query))
            self.assertIsNone(g1.value(ls, R2RML.tableName))

    def test_natural_sql_datatypes(self) -> None:
        """
        Test adding SQL datatypes to PredicateObjectMaps.
        """
        p1 = 'tests/assets/io/mapping_files/mapping_sql_datatypes.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_sql_datatypes_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        f = NamedTemporaryFile(delete=False)
        g1.serialize(f.name, format='turtle')
        print(f.name)
        self.assertEqual(g1, g2, 'SQL datatypes not correctly added!')

    def test_rewrite_rr_graph_map(self) -> None:
        """
        Test rewriting rr:graphMap from SubjectMap to all PredicateObjectMaps.
        """
        p1 = 'tests/assets/io/mapping_files/mapping_rr_graph_map.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_rr_graph_map_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        self.assertEqual(g1, g2, 'rr:graph not correctly rewritten!')

    def test_rewrite_rr_class(self) -> None:
        """
        Test rewriting rr:class of a SubjectMap into rdf:type PredicateMap.
        """
        p1 = 'tests/assets/io/mapping_files/mapping_rr_class.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_rr_class_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        self.assertEqual(g1, g2, 'rr:class not correctly rewritten!')

    def test_rr_table_name_fallback(self) -> None:
        """
        Test if we fallback to SELECT * FROM <table> if no columns were
        extracted for the TriplesMap.
        """
        p1 = 'tests/assets/io/mapping_files/mapping_rr_table_name_fallback.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_rr_table_name_fallback_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        self.assertEqual(g1, g2, 'rr:tableName fallback failed!')

    def test_empty_table_warning(self) -> None:
        """
        Test if we print a warning when an empty table is used for determining
        the datatypes
        """
        p1 = 'tests/assets/io/mapping_files/mapping_empty_table.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_empty_table_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        self.assertEqual(g1, g2, 'Empty table warning failed!')

    def test_unknown_column(self) -> None:
        """
        Test if unknown columns are skipped when adding datatypes.
        """
        p1 = 'tests/assets/io/mapping_files/mapping_unknown_column.ttl'
        p2 = 'tests/assets/io/mapping_files/mapping_unknown_column_compiled.ttl'
        g1, g2 = self._compile_rules(p1, p2)
        self.assertEqual(g1, g2, 'Unknown column not skipped!')

    def test_operational_error_sql(self) -> None:
        """
        Test if a ValueError is raised when SQL has an OperationalError.
        """
        p = 'tests/assets/io/mapping_files/mapping_operational_error.ttl'
        with self.assertRaises(ValueError):
            m = MappingCompiler()
            m.compile(Graph().parse(p, format='turtle'))


if __name__ == '__main__':
    unittest.main()
