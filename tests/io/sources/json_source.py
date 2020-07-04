#!/usr/bin/env python

import unittest
from json.decoder import JSONDecodeError

from rml.io.sources.json_source import JSONLogicalSource



class JSONLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator(self) -> None:
        """
        Test if we can iterate over the results of the JSONPath expression
        """
        self.source = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        self.assertDictEqual(next(self.source),
                             {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(self.source),
                             {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(self.source),
                             {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_file(self) -> None:
        """
        Test if we raise a FileNotFoundError exception when the input file does
        not exist
        """
        with self.assertRaises(FileNotFoundError):
            self.source = JSONLogicalSource('$.students.[*]', 'this/file/does/not/exist')

    def test_invalid_jsonpath(self) -> None:
        """
        Test if we raise a ValueError when the JSONPath expression is invalid
        """
        with self.assertRaises(ValueError):
            self.source = JSONLogicalSource('&$"£*W$', 'tests/assets/json/student.json')

    def test_invalid_json(self) -> None:
        """
        Test if we raise a JSONDecodeError when the input file cannot be parsed
        as valid JSON
        """
        with self.assertRaises(JSONDecodeError):
            self.source = JSONLogicalSource('$.students.[*]', 'tests/assets/json/invalid.json')

    def test_empty_iterator(self) -> None:
        """
        Test if we handle an empty iterator
        """
        with self.assertRaises(StopIteration):
            self.source = JSONLogicalSource('$.empty', 'tests/assets/json/student.json')
            next(self.source)

if __name__ == '__main__':
    unittest.main()
