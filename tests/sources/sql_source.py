#!/usr/bin/env python

import unittest
from sqlalchemy.exc import OperationalError

from rml.sources import SQLLogicalSource

class SQLLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator(self) -> None:
        """
        Test if we can iterate over every row
        """
        self.source = SQLLogicalSource('sqlite:///tests/assets/sql/student.db', 
                                       'SELECT id, name, age FROM students;')
        self.assertDictEqual(next(self.source),
                             {'id': 0, 'name': 'Herman', 'age': 65})
        self.assertDictEqual(next(self.source),
                             {'id': 1, 'name': 'Ann', 'age': 62})
        self.assertDictEqual(next(self.source),
                             {'id': 2, 'name': 'Simon', 'age': 23})
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_database(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the input file
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            self.source = SQLLogicalSource('sqlite:///this/file/does/not/exist',
                                           'SELECT id, name, age FROM students;')

    def test_non_existing_table(self) -> None:
        """
        Test if we raise an ValueError when the table does not exist
        """
        with self.assertRaises(ValueError):
            self.source = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                                           'SELECT id, name, age FROM empty;')
            next(self.source)

    def test_non_existing_column(self) -> None:
        """
        Test if we raise an ValueError when the column does not exist
        """
        with self.assertRaises(ValueError):
            self.source = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                                           'SELECT empty FROM students;')
            next(self.source)

    def test_empty_iterator(self) -> None:
        """
        Test if we can handle an empty iterator (table)
        """
        with self.assertRaises(StopIteration):
            self.source = SQLLogicalSource('sqlite:///tests/assets/sql/empty.db',
                                           'SELECT id, name, age FROM students;')

if __name__ == '__main__':
    unittest.main()
