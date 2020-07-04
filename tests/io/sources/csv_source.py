#!/usr/bin/env python

import unittest

from rml.io.sources import CSVLogicalSource


class CSVLogicalSourceTests(unittest.TestCase):
    def test_iterator(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = CSVLogicalSource('tests/assets/csv/student.csv')
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
        Test if a FileNotFoundError exception is raised when the input file
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            source = CSVLogicalSource('this/file/does/not/exist')
            next(source)

    def test_empty_iterator(self) -> None:
        """
        Test if we can handle an empty CSV file
        """
        with self.assertRaises(StopIteration):
            source = CSVLogicalSource('tests/assets/csv/empty.csv')
            next(source)

    def test_missing_header(self) -> None:
        """
        Test if we raise a ValueError when no CSV header is available
        """
        with self.assertRaises(ValueError):
            source = CSVLogicalSource('tests/assets/csv/no_header.csv')
            next(source)

    def test_delimiter(self) -> None:
        """
        Test if we can handle different delimiters such as TABS in TSV files.
        """
        source = CSVLogicalSource('tests/assets/csv/student.tsv',
                                       delimiter='\t')
        self.assertDictEqual(next(source),
                             {'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertDictEqual(next(source),
                             {'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertDictEqual(next(source),
                             {'id': '2', 'name': 'Simon', 'age': '23'})
        with self.assertRaises(StopIteration):
            next(source)

if __name__ == '__main__':
    unittest.main()
