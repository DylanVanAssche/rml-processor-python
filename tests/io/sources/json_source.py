#!/usr/bin/env python

import unittest
from json.decoder import JSONDecodeError

from rml.io.sources.json_source import JSONLogicalSource



class JSONLogicalSourceTests(unittest.TestCase):
    def test_iterator(self) -> None:
        """
        Test if we can iterate over the results of the JSONPath expression
        """
        source = JSONLogicalSource('$.students.[*]', 'tests/assets/json/student.json')
        self.assertDictEqual(next(source),
                             {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(source),
                             {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(source),
                             {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(source)

    def test_non_existing_file(self) -> None:
        """
        Test if we raise a FileNotFoundError exception when the input file does
        not exist
        """
        with self.assertRaises(FileNotFoundError):
            source = JSONLogicalSource('$.students.[*]', 'this/file/does/not/exist')

    def test_invalid_jsonpath(self) -> None:
        """
        Test if we raise a ValueError when the JSONPath expression is invalid
        """
        with self.assertRaises(ValueError):
            source = JSONLogicalSource('&$"£*W$', 'tests/assets/json/student.json')

    def test_invalid_json(self) -> None:
        """
        Test if we raise a JSONDecodeError when the input file cannot be parsed
        as valid JSON
        """
        with self.assertRaises(JSONDecodeError):
            source = JSONLogicalSource('$.students.[*]', 'tests/assets/json/invalid.json')

    def test_empty_iterator(self) -> None:
        """
        Test if we handle an empty iterator
        """
        with self.assertRaises(StopIteration):
            source = JSONLogicalSource('$.empty', 'tests/assets/json/student.json')
            next(source)

if __name__ == '__main__':
    unittest.main()
