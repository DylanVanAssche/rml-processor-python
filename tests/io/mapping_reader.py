import unittest
from rml.io.mapping_reader import MappingReader

class MappingReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mapping_reader = MappingReader()

    def tearDown(self) -> None:
        del self.mapping_reader

    def test_read(self) -> None:
        path = 'tests/assets/io/mapping_files/mapping_001.ttl'
        result = self.mapping_reader.read(path)
        self.assertGreater(len(result), 0)

    def test_non_existing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            path = '/this/file/does/not/exist.ttl'
            result = self.mapping_reader.read(path)

    def test_invalid_turtle(self) -> None:
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/invalid.ttl'
            result = self.mapping_reader.read(path)

    def test_invalid_format(self) -> None:
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/mapping_001.rdf'
            result = self.mapping_reader.read(path)

if __name__ == '__main__':
    unittest.main()
