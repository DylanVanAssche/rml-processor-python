#!/usr/bin/env python

import unittest

from sources import CSVLogicalSource

class CSVLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = CSVLogicalSource('tests/assets/csv/student.csv')

    def test_iterator(self) -> None:
        self.assertDictEqual(next(self.source),
                            {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(self.source),
                            {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(self.source),
                            {'id': '2', 'name': 'Simon', 'age': '23'})

if __name__ == '__main__':
    unittest.main()
