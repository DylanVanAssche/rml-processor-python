#!/usr/bin/env python

import unittest
from parameterized import parameterized
from typing import List, Dict

from rml.io.sources import CSVLogicalSource, MIMEType, CSVWTrimMode, CSVColumn


class CSVLogicalSourceTests(unittest.TestCase):
    def test_iterator(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = CSVLogicalSource('tests/assets/csv/student.csv')
        self.assertDictEqual(next(source),
                             {'id': '0', 'name': 'Herman', 'age': '65',
                              'iri': 'http://example.com/myStudent1'})
        self.assertDictEqual(next(source),
                             {'id': '1', 'name': 'Ann', 'age': '62',
                              'iri': 'http://example.com/myStudent2'})
        self.assertDictEqual(next(source),
                             {'id': '2', 'name': 'Simon', 'age': '23',
                              'iri': 'http://example.com/myStudent3'})
        with self.assertRaises(StopIteration):
            next(source)

    def test_mime_type(self) -> None:
        """
        Test the MIME type property
        """
        source = CSVLogicalSource('tests/assets/csv/student.csv')
        self.assertEqual(source.mime_type, MIMEType.CSV)

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
        # Catch failure when header is provided through RML rules
        with self.assertRaises(ValueError):
            source = CSVLogicalSource('tests/assets/csv/no_header.csv',
                    has_header=False)
            next(source)

        # Catch failure when header is provided through CSV file
        with self.assertRaises(ValueError):
            source = CSVLogicalSource('tests/assets/csv/no_header.csv',
                    has_header=True)
            next(source)

    def test_dialect_delimiter(self) -> None:
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

    @parameterized.expand([
        [CSVLogicalSource('tests/assets/csv/student.tsv', delimiter='\t'),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/double_quote.csv',
                          double_quote=True),
         [{'id': '0', 'name': '"Herman"', 'age': '65'},
          {'id': '1', 'name': '"Ann"', 'age': '62'},
          {'id': '2', 'name': '"Simon"', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/escape_char.csv', escape_char='%'),
         [{'id': '0', 'name': 'Herman,', 'age': '65'},
          {'id': '1', 'name': 'Ann,', 'age': '62'},
          {'id': '2', 'name': 'Simon,', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/line_terminators.csv',
                          line_terminators='\r\n'),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/quote_char.csv', quote_char='^'),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/trim_mode_start_and_end.csv',
                          trim_mode=CSVWTrimMode.START_AND_END),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/trim_mode_start.csv',
                          trim_mode=CSVWTrimMode.START),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/trim_mode_end.csv',
                          trim_mode=CSVWTrimMode.END),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/trim_mode_none.csv',
                          trim_mode=CSVWTrimMode.NONE),
         [{'id': '0', 'name': '  Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann  ', 'age': '62'},
          {'id': '2', 'name': '  Simon  ', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/skip_initial_space.csv',
                          skip_initial_space=True),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/has_no_header.csv',
                          has_header=False, header_row_count=0,
                          header=[CSVColumn('id', '-1'), CSVColumn('name', ''),
                                  CSVColumn('age', '0')]),
         [{'id': None, 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': None},
          {'id': '2', 'name': None, 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/has_header_overide.csv',
                          has_header=True, header_row_count=1,
                          header=[CSVColumn('id', '-1'), CSVColumn('name', ''),
                                  CSVColumn('age', '0')]),
         [{'id': None, 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': None},
          {'id': '2', 'name': None, 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/skip_columns.csv', skip_columns=1),
         [{'name': 'Herman', 'age': '65'},
          {'name': 'Ann', 'age': '62'},
          {'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/skip_rows.csv', skip_rows=1),
         [{'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/comment_prefix.csv',
                          comment_prefix='$'),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/encoding.csv',
                          encoding='utf-16'),
         [{'id': '0', 'name': 'Herman', 'age': '65'},
          {'id': '1', 'name': 'Ann', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
        [CSVLogicalSource('tests/assets/csv/dialect_mix.csv',
                          double_quote=True,
                          trim_mode=CSVWTrimMode.START_AND_END,
                          skip_initial_space=True, has_header=True,
                          comment_prefix='$'),
         [{'id': '0', 'name': '"Herman"', 'age': '65'},
          {'id': '1', 'name': '"Ann"', 'age': '62'},
          {'id': '2', 'name': 'Simon', 'age': '23'}]
        ],
    ])
    def test_dialect(self, source: CSVLogicalSource,
                     expected_data: List[Dict]) -> None:
        """
        Test if we can handle CSV dialects.
        Parameterized for all possible dialect settings of CSVW.
        """
        print(source._path)
        self.assertDictEqual(next(source), expected_data[0])
        self.assertDictEqual(next(source), expected_data[1])
        # Skip row test skips the first row so only 2 rows can be fetched
        if 'skip_rows.csv' not in source._path:
            self.assertDictEqual(next(source), expected_data[2])
        with self.assertRaises(StopIteration):
            next(source)

    def test_null_value(self) -> None:
        """
        Test if null values are properly replaced by None
        """
        expected_data = {'id': None, 'name': 'Herman', 'age': '65'}
        source = CSVLogicalSource('tests/assets/csv/null_value.csv',
                                  header=[CSVColumn('id', '-1'),
                                          CSVColumn('name'),
                                          CSVColumn('age', '0')])
        self.assertDictEqual(next(source), expected_data)
        with self.assertRaises(StopIteration):
            next(source)

    def test_header_count_invalid(self) -> None:
        """
        Test if we raise a ValueError when the header row count is 0 but a
        header is provided (has header)
        """
        with self.assertRaises(ValueError):
            CSVLogicalSource('tests/assets/csv/student.csv', has_header=True,
                    header_row_count=0)


if __name__ == '__main__':
    unittest.main()
