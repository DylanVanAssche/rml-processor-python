import unittest
from rml.io.mapping_reader import MappingReader


class MappingReaderTests(unittest.TestCase):

    def setUp(self):
        self.mapping_reader = MappingReader()

    def tearDown(self):
        del self.mapping_reader

    def test_read(self):
        path = 'tests/assets/io/mapping_files/mapping_001.ttl'
        result = self.mapping_reader.read(path)
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
