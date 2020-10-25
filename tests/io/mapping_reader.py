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
        expected_triples = to_isomorphic(expected_triples)
        self.assertEqual(generated_triples,
                         expected_triples,
                         msg='Difference:\n '
                         f'{graph_diff(generated_triples, expected_triples)}')

    def test_retrieve_rules(self) -> None:
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
        expected_triples = ConjunctiveGraph().parse(output_path,
                                                    format='nquads')
        # Compatible with CI and local deployment: replace 127.0.0.1 with the
        # host at runtime.
        rules_with_host = NamedTemporaryFile(mode='w', delete=False)
        with open(rules_path, 'r') as f:
            temp = f.read().replace('127.0.0.1', HOST)
            print(temp)
            rules_with_host.write(temp)
        rules_with_host.close()
        print(rules_with_host.name)

        # Run test
        mapping_reader = MappingReader(rules_with_host.name)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list, expected_triples)

    def test_read_unknown_source(self) -> None:
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/mapping_unknown_source.ttl'
            mapping_reader = MappingReader(path)
            tm_list = mapping_reader.resolve()

    def test_non_existing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            path = '/this/file/does/not/exist.ttl'
            mapping_reader = MappingReader(path)
            result = mapping_reader.rules

    def test_invalid_turtle(self) -> None:
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/invalid.ttl'
            mapping_reader = MappingReader(path)
            result = mapping_reader.rules

    def test_invalid_format(self) -> None:
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/mapping_001.rdf'
            mapping_reader = MappingReader(path)
            result = mapping_reader.rules

if __name__ == '__main__':
    unittest.main()
