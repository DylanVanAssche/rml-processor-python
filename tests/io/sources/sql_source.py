#!/usr/bin/env python

import unittest
from sqlalchemy.exc import OperationalError

from rml.io.sources import SQLLogicalSource, MIMEType

class SQLLogicalSourceTests(unittest.TestCase):
    def test_mime_type(self) -> None:
        """
        Test the MIME type property
        """
        source = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                                       'SELECT id, name, age FROM students;')
        self.assertEqual(source.mime_type, MIMEType.SQL)

    def test_iterator(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                                       'SELECT id, name, age FROM students;')
        self.assertDictEqual(next(source),
                             {'id': 0, 'name': 'Herman', 'age': 65})
        self.assertDictEqual(next(source),
                             {'id': 1, 'name': 'Ann', 'age': 62})
        self.assertDictEqual(next(source),
                             {'id': 2, 'name': 'Simon', 'age': 23})
        with self.assertRaises(StopIteration):
            next(source)

    def test_non_existing_database(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the input file
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            source = SQLLogicalSource('sqlite:///this/file/does/not/exist',
                                           'SELECT id, name, age FROM students;')

    def test_non_existing_table(self) -> None:
        """
        Test if we raise an ValueError when the table does not exist
        """
        with self.assertRaises(ValueError):
            source = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                                           'SELECT id, name, age FROM empty;')
            next(source)

    def test_non_existing_column(self) -> None:
        """
        Test if we raise an ValueError when the column does not exist
        """
        with self.assertRaises(ValueError):
            source = SQLLogicalSource('sqlite:///tests/assets/sql/student.db',
                                           'SELECT empty FROM students;')
            next(source)

    def test_empty_iterator(self) -> None:
        """
        Test if we can handle an empty iterator (table)
        """
        with self.assertRaises(StopIteration):
            source = SQLLogicalSource('sqlite:///tests/assets/sql/empty.db',
                                           'SELECT id, name, age FROM students;')
            next(source)

if __name__ == '__main__':
    unittest.main()
