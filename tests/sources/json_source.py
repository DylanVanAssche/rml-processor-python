#!/usr/bin/env python

import unittest
from json.decoder import JSONDecodeError

from rml.sources import JSONLogicalSource

class JSONLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator(self) -> None:
        self.source = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        self.assertDictEqual(next(self.source).value,
                             {'id': '0', 'name': 'Herman', 'age': 65})
        self.assertDictEqual(next(self.source).value,
                             {'id': '1', 'name': 'Ann', 'age': 62})
        self.assertDictEqual(next(self.source).value,
                             {'id': '2', 'name': 'Simon', 'age': 23})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.source = JSONLogicalSource('$.students.[*]', 'this/file/does/not/exist')

    def test_invalid_jsonpath(self) -> None:
        self.source = JSONLogicalSource('abc', 'tests/assets/json/student.json')

    def test_invalid_json(self) -> None:
        with self.assertRaises(JSONDecodeError):
            self.source = JSONLogicalSource('$.students.[*]', 'tests/assets/json/invalid.json')

    def test_empty_iterator(self) -> None:
        self.source = JSONLogicalSource('$.empty', 'tests/assets/json/student.json')
        with self.assertRaises(StopIteration):
            next(self.source)

if __name__ == '__main__':
    unittest.main()
