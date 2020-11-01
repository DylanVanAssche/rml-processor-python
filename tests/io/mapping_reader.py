import unittest
from parameterized import parameterized
from tempfile import NamedTemporaryFile
from os import environ
from typing import List, Tuple, Set
from rdflib import ConjunctiveGraph, Graph
from rdflib.compare import to_isomorphic, graph_diff

from rml.io.mapping_reader import MappingReader
from rml.io.maps import TriplesMap

HOST = environ['HOST']


class MappingReaderTests(unittest.TestCase):
    def _process_tm_results(self, tm_list: List[TriplesMap],
                            expected_triples: ConjunctiveGraph) -> None:
        """
        Process the TriplesMap's results and compare it with what we expect.
        """
        self.assertGreater(len(tm_list), 0)
        generated_triples = ConjunctiveGraph()
        for tm in tm_list:
            while True:
                try:
                    for t in next(tm):
                        # No Named Graph specified
                        if t[3] is None:
                            generated_triples.add(t)
                        else:
                            generated_triples.addN(t)
                except StopIteration:
                    break
        generated_triples = to_isomorphic(generated_triples)
        from tempfile import NamedTemporaryFile
        f = NamedTemporaryFile(delete=False, mode='wb')
        generated_triples.serialize(f.name, format='nquads')
        print(f.name)
        expected_triples = to_isomorphic(expected_triples)
        self.assertEqual(generated_triples,
                         expected_triples,
                         msg='Difference:\n '
                         f'{graph_diff(generated_triples, expected_triples)}')

    def test_retrieve_rules(self) -> None:
        """
        Test reading rules without checking the output or executing them.
        """
        path = 'tests/assets/io/mapping_files/mapping_local_file.ttl'
        mapping_reader = MappingReader(path)
        self.assertIsInstance(mapping_reader.rules, Graph)

    @parameterized.expand([
        ('tests/assets/io/mapping_files/mapping_local_file.ttl',
         'tests/assets/io/output_files/output_local_file.nq'),
        ('tests/assets/io/mapping_files/mapping_dcat.ttl',
         'tests/assets/io/output_files/output_dcat.nq'),
        ('tests/assets/io/mapping_files/mapping_sql.ttl',
         'tests/assets/io/output_files/output_sql.nq'),
        ('tests/assets/io/mapping_files/mapping_sparql.ttl',
         'tests/assets/io/output_files/output_sparql.nq'),
        ('tests/assets/io/mapping_files/mapping_edge_case.ttl',
         'tests/assets/io/output_files/output_edge_case.nq'),
        ('tests/assets/io/mapping_files/mapping_shortcuts.ttl',
         'tests/assets/io/output_files/output_shortcuts.nq'),
        ('tests/assets/io/mapping_files/mapping_class.ttl',
         'tests/assets/io/output_files/output_class.nq')
    ])
    def test_read_source(self, rules_path: str, output_path: str) -> None:
        """
        Tests reading all the Logical Sources supported by this processor.
        Mapping compilation is automatically tested with this test since it's
        integrated into the mapping reader
        """
        expected_triples = ConjunctiveGraph().parse(output_path,
                                                    format='nquads')
        # Compatible with CI and local deployment: replace 127.0.0.1 with the
        # host at runtime.
        rules_with_host = NamedTemporaryFile(mode='w', delete=False)
        with open(rules_path, 'r') as f:
            temp = f.read().replace('127.0.0.1', HOST)
            rules_with_host.write(temp)
        rules_with_host.close()

        # Run test
        mapping_reader = MappingReader(rules_with_host.name)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list, expected_triples)

    @parameterized.expand([
        ('tests/assets/io/mapping_files/mapping_csv_delimiter.ttl',
         'tests/assets/io/output_files/output_csv_delimiter.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_double_quote.ttl',
         'tests/assets/io/output_files/output_csv_double_quote.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_escape_char.ttl',
         'tests/assets/io/output_files/output_csv_escape_char.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_line_terminators.ttl',
         'tests/assets/io/output_files/output_csv_line_terminators.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_quote_char.ttl',
         'tests/assets/io/output_files/output_csv_quote_char.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_trim_mode_start_and_end1.ttl',
         'tests/assets/io/output_files/output_csv_trim_mode_start_and_end.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_trim_mode_start_and_end2.ttl',
         'tests/assets/io/output_files/output_csv_trim_mode_start_and_end.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_trim_mode_start.ttl',
         'tests/assets/io/output_files/output_csv_trim_mode_start.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_trim_mode_end.ttl',
         'tests/assets/io/output_files/output_csv_trim_mode_end.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_trim_mode_none1.ttl',
         'tests/assets/io/output_files/output_csv_trim_mode_none.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_trim_mode_none2.ttl',
         'tests/assets/io/output_files/output_csv_trim_mode_none.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_skip_initial_space.ttl',
         'tests/assets/io/output_files/output_csv_skip_initial_space.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_has_no_header.ttl',
         'tests/assets/io/output_files/output_csv_has_no_header.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_has_header_overide.ttl',
         'tests/assets/io/output_files/output_csv_has_header_overide.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_skip_columns.ttl',
         'tests/assets/io/output_files/output_csv_skip_columns.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_skip_rows.ttl',
         'tests/assets/io/output_files/output_csv_skip_rows.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_comment_prefix.ttl',
         'tests/assets/io/output_files/output_csv_comment_prefix.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_encoding.ttl',
         'tests/assets/io/output_files/output_csv_encoding.nq'),
        ('tests/assets/io/mapping_files/mapping_csv_dialect_mix.ttl',
         'tests/assets/io/output_files/output_csv_dialect_mix.nq'),
    ])
    def test_read_csv_dialects(self, rules_path: str, output_path: str)\
            -> None:
        """
        Test reading various CSV dialects.
        """
        expected_triples = ConjunctiveGraph().parse(output_path,
                                                    format='nquads')
        mapping_reader = MappingReader(rules_path)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list, expected_triples)

    def test_read_unknown_source(self) -> None:
        """
        Test if a ValueError is raised when an unknown Logical Source has been
        found in the rules.
        """
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/mapping_unknown_source.ttl'
            mapping_reader = MappingReader(path)
            tm_list = mapping_reader.resolve()

    def test_non_existing_file(self) -> None:
        """
        Test if a FileNotFoundError is raised when the rules cannot be found.
        """
        with self.assertRaises(FileNotFoundError):
            path = '/this/file/does/not/exist.ttl'
            mapping_reader = MappingReader(path)
            result = mapping_reader.rules

    def test_invalid_turtle(self) -> None:
        """
        Test if a ValueError is raised when the rules are invalid Turtle.
        """
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/invalid.ttl'
            mapping_reader = MappingReader(path)
            result = mapping_reader.rules

    def test_invalid_format(self) -> None:
        """
        Test if a ValueError is raised when the rules are written in a
        different format than Turtle.
        """
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/mapping_001.rdf'
            mapping_reader = MappingReader(path)
            result = mapping_reader.rules

if __name__ == '__main__':
    unittest.main()
