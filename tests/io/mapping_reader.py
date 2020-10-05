import unittest
from typing import List
from rdflib import Graph

from rml.io.mapping_reader import MappingReader
from rml.io.maps import TriplesMap


class MappingReaderTests(unittest.TestCase):
    def _process_tm_results(self, tm_list: List[TriplesMap]) -> None:
        self.assertGreater(len(tm_list), 0)

        tm_exhausted: int = 0
        while tm_exhausted < len(tm_list):
            for tm in tm_list:
                try:
                    triples = next(tm)
                    print(triples)
                except StopIteration:
                    tm_exhausted = tm_exhausted + 1

    def test_retrieve_rules(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_local_file.ttl'
        mapping_reader = MappingReader(path)
        self.assertIsInstance(mapping_reader.rules, Graph)

    def test_read_local_file(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_local_file.ttl'
        mapping_reader = MappingReader(path)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list)

    def test_read_dcat(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_dcat.ttl'
        mapping_reader = MappingReader(path)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list)

    def test_read_sql(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_sql.ttl'
        mapping_reader = MappingReader(path)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list)

    def test_read_sparql(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_sparql.ttl'
        mapping_reader = MappingReader(path)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list)

    def test_read_edge_case(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_edge_case.ttl'
        mapping_reader = MappingReader(path)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list)

    def test_read_shortcuts(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_shortcuts.ttl'
        mapping_reader = MappingReader(path)
        tm_list = mapping_reader.resolve()
        self._process_tm_results(tm_list)
        self.assertTrue(tm_list)

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
