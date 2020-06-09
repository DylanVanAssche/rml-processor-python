#!/usr/bin/env python

import unittest

from rml.sources import CSVLogicalSource

class CSVLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator(self) -> None:
        self.source = CSVLogicalSource('tests/assets/csv/student.csv')
        self.assertDictEqual(next(self.source),
                            {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(self.source),
                            {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(self.source),
                            {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.source = CSVLogicalSource('this/file/does/not/exist')

if __name__ == '__main__':
    unittest.main()
