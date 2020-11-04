from enum import Enum
from itertools import filterfalse
from logging import debug, info, warning, error, critical
from typing import Iterator, IO, Dict, Optional, List, cast
from rdflib.term import URIRef
from csv import DictReader, Sniffer, Error, QUOTE_ALL, QUOTE_NONE, \
        QUOTE_MINIMAL, QUOTE_NONNUMERIC

from rml.io.sources import LogicalSource, MIMEType
from rml.namespace import XSD, RDF, CSVW

# Bytes to sniff to detect the CSV header
BYTES_TO_SNIFF = 1024
# Default values according to the CSVW specification
DEFAULT_NULL_VALUE: str = ''
DEFAULT_DELIMITER: str = ','
DEFAULT_QUOTE_CHAR: str = '"'
DEFAULT_LINE_TERMINATORS: str = '\r\n'
DEFAULT_DOUBLE_QUOTE: bool = True
DEFAULT_QUOTING: int = QUOTE_MINIMAL
DEFAULT_SKIP_INITIAL_SPACE: bool = False
DEFAULT_HAS_HEADER: bool = True
DEFAULT_HEADER_ROW_COUNT: int = 1
DEFAULT_SKIP_COLUMNS: int = 0
DEFAULT_SKIP_ROWS: int = 0
DEFAULT_COMMENT_PREFIX: str = '#'
DEFAULT_ENCODING: str = 'utf-8'
# Custom escape character is not part of the CSVW specification
DEFAULT_ESCAPE_CHAR: Optional[str] = None


class CSVWTrimMode(Enum):
    """
    CSVW defines 4 trim modes:
        - no trimming
        - start (same as skip_initial_space)
        - end
        - start and end (default)
    """
    NONE = 'false'
    START = 'start'
    END = 'end'
    START_AND_END = 'true'


# CSVW default value for csvw:trim
DEFAULT_TRIM_MODE = CSVWTrimMode.NONE


class CSVColumn:
    """
    CSV Column to describe the properties of the CSV column for parsing.
    Default null value for column: ''
    """
    def __init__(self, name: str,
                 null_value: str = DEFAULT_NULL_VALUE) -> None:
        """
        Creates CSVColumn with a name and null value.

        :param str name: Name of the column
        :param str null_value: The value to use to indicate that the column
        value should be used as a NULL value.
        :return None
        """
        self._name: str = name
        self._null_value: str = null_value
        debug(f'Name: {self._name}')
        debug(f'Null value: {self._null_value}')
        debug('CSVWColumn initialization complete')

    @property
    def name(self) -> str:
        """
        The name of the CSV column.
        :return str name
        """
        return self._name

    @property
    def null_value(self) -> str:
        """
        The null value to use for the CSV column.
        :return str null_value
        """
        return self._null_value


# By default, the header is provided in the CSV file, hence []
DEFAULT_HEADER: List[CSVColumn] = []


class CSVLogicalSource(LogicalSource):
    """
    An RML Logical Source to read CSV files.
    """
    def __init__(self, path: str,
                 delimiter: str = DEFAULT_DELIMITER,
                 double_quote: bool = DEFAULT_DOUBLE_QUOTE,
                 escape_char: Optional[str] = DEFAULT_ESCAPE_CHAR,
                 line_terminators: str = DEFAULT_LINE_TERMINATORS,
                 quote_char: str = DEFAULT_QUOTE_CHAR,
                 quoting: int = DEFAULT_QUOTING,
                 trim_mode: CSVWTrimMode = DEFAULT_TRIM_MODE,
                 skip_initial_space: bool = DEFAULT_SKIP_INITIAL_SPACE,
                 has_header: bool = DEFAULT_HAS_HEADER,
                 header_row_count: int = DEFAULT_HEADER_ROW_COUNT,
                 header: List[CSVColumn] = DEFAULT_HEADER,
                 skip_columns: int = DEFAULT_SKIP_COLUMNS,
                 skip_rows: int = DEFAULT_SKIP_ROWS,
                 comment_prefix: str = DEFAULT_COMMENT_PREFIX,
                 encoding: str = DEFAULT_ENCODING):
        """
        A CSV Logical Source to iterate over CSV data.
        The RML iterator is not used for row-based iterators.

        :param str path: The file path to the CSV file.
        :param str delimiter: The delimiter used in the CSV file.
        :param bool doube_quote: If a quote character must be escaped, it can
        be double quoted (if True) or escaped using the escape character (if
        False).
        :param str escape_char: Escape character to use.
        :param str line_terminators: End of line characters.
        :param str quote_char: Character to indicate the start and end of
        quoting.
        :param int quoting: The quoting mode to use: QUOTE_ALL, QUOTE_NONE,
        QUOTE_MINIMAL, QUOTE_NONNUMERIC.
        :param CSVWTrimMode trim_mode: The trimming mode to use for the CSV
        values.
        :param bool skip_initial_space: Enable skipping initial spacing of CSV
        values. This is ignored if trim_mode is not set to CSVWTrimMode.NONE.
        :param bool has_header: Indicates if the header is provided in the CSV
        file itself.
        :param int header_row_count: The number of CSV rows to use as header.
        :param int skip_columns: The number of columns that need to be skipped.
        Example: 3 means that the first 3 columns are not processed.
        :param int skip_rows: The number of rows that need to be skipped.
        Example: 2 means that the first 2 rows are not processed.
        :param str comment_prefix: Indicates which character is used for
        comments.
        :param str encoding: File encoding to use

        note: CSVW Dialect's skip blank rows is not supported since blank rows
        are always ignored when processing the CSV file.

        warning: The Python CSV reader has hardcoded line terminators. Setting
        the line terminator will not influence the way the CSV file is read.
        seealso: https://docs.python.org/3/library/csv.html#csv.Dialect.lineterminator  # noqa
        """
        super().__init__()
        self._path: str = path
        self._delimiter: str = delimiter
        self._double_quote: bool = double_quote
        self._escape_char: Optional[str] = escape_char
        self._line_terminators: str = line_terminators
        self._quote_char: str = quote_char
        self._quoting: int = quoting
        self._skip_initial_space: bool = skip_initial_space
        self._has_header: bool = has_header
        self._header_row_count: int = header_row_count
        self._header: List[CSVColumn] = header
        self._trim_mode: CSVWTrimMode = trim_mode
        self._skip_columns: int = skip_columns
        self._skip_rows: int = skip_rows
        self._column_names: Optional[List[str]] = None
        self._comment_prefix: str = comment_prefix
        self._encoding: str = encoding
        self._null_values: Dict = {}
        debug(f'Path: {self._path}')
        debug(f'Delimiter: {self._delimiter}')
        debug(f'Double quote: {self._double_quote}')
        debug(f'Escape char: {self._escape_char}')
        debug(f'Line terminator: {self._line_terminators}')
        debug(f'Quote char: {self._quote_char}')
        debug(f'Quoting: {self._quoting}')
        debug(f'Skip initial space: {self._skip_initial_space}')
        debug(f'Has header: {self._has_header}')
        debug(f'Header row count: {self._header_row_count}')
        debug(f'Trim mode: {self._trim_mode}')
        debug(f'Skip columns: {self._skip_columns}')
        debug(f'Skip rows: {self._skip_rows}')
        debug(f'Comment prefix: {self._comment_prefix}')
        debug(f'Encoding: {self._encoding}')

        # If trimming is enabled, skip initial space is disabled (CSVW spec)
        if self._trim_mode != CSVWTrimMode.NONE:
            self._skip_initial_space = False

        # If header is included in the CSV file, header row count must be >= 1
        if self._has_header and self._header_row_count <= 0:
            msg = 'Header row count must be >= 1 if CSV file has a header, '
            'falling back to header row count = 1'
            error(msg)
            raise ValueError(msg)

        # If no header is included in the CSV file, force header_row_count to 0
        if not self._has_header:
            self._header_row_count = 0

        # Header is provided as metadata
        if self._header:
            self._column_names = []
            self._null_values = {}
            for c in self._header:
                self._column_names.append(c.name)
                self._null_values[c.name] = c.null_value
            debug(f'Provided header: {self._column_names} from {self._path}')

            # Overide of existing header, skipping it
            if self._has_header:
                info(f'Overide of header, skipping {self._header_row_count} '
                     'header rows')
                self._skip_rows += self._header_row_count
            else:
                info('No header in CSV file, not skipping any header rows')

        # Check the header's existence
        elif self._has_header:
            with open(self._path, encoding=self._encoding) as f:
                sniffer: Sniffer = Sniffer()
                try:
                    if not sniffer.has_header(f.read(BYTES_TO_SNIFF)):
                        msg = 'CSV file requires a header'
                        critical(msg)
                        raise ValueError(msg)
                # Sniffer raises Error when delimiter cannot be determined
                except Error as e:  # pragma: no cover
                    warning('Unable to determine delimiter, falling back to '
                            f'default ({DEFAULT_DELIMITER}): {e}')
            debug(f'Detected CSV header in {self._path}')
        # No header in the CSV file or provided as metadata, abort!
        else:
            msg = 'CSV file requires a header'
            critical(msg)
            raise ValueError(msg)

        # Create CSV file iterator
        self._file: IO = open(self._path, encoding=self._encoding)

        # Filter out comments
        debug(f'Filtering out comments with prefix: {self._comment_prefix}')
        self._iterator: Iterator = filterfalse(lambda r: r.lstrip()
                .startswith(self._comment_prefix), self._file)  # noqa

        # Configure CSV DictReader with the provided CSV dialect
        self._iterator = DictReader(self._iterator,
                                    fieldnames=self._column_names,
                                    delimiter=self._delimiter,
                                    doublequote=self._double_quote,
                                    escapechar=self._escape_char,
                                    lineterminator=self._line_terminators,
                                    quotechar=self._quote_char,
                                    quoting=self._quoting,
                                    skipinitialspace=self._skip_initial_space)

        # Skip a number of rows if skip_rows > 0
        for i in range(0, self._skip_rows):
            debug(f'Skipping row: {i}')
            next(self._iterator)

        # Skip first number of columns if needed
        self._iterator = self._filter_columns(self._iterator)

        debug('Source initialization complete')

    def __next__(self) -> Dict:
        """
        Returns a row from the CSV iterator.
        raises StopIteration when exhausted.
        """
        try:
            result: Dict = next(self._iterator)
            result = self._trim_result(result)
            result = self._replace_null_values(result)
            debug(f'Iterator: {result}')
            return result
        # Iterator exhausted
        except StopIteration:
            self._file.close()
            debug('File closed')
            raise StopIteration

    def _filter_columns(self, iterator: DictReader) -> Iterator:
        """
        A generator to filter out columns which for skip_columns
        https://stackoverflow.com/questions/7880391/python-csv-dictreader-ignore-columns

        :param iter iterator: The iterator to filter on
        :returns iter iterator: filtered iterator
        """
        # Handle missing column names, fallback, catched above
        if iterator.fieldnames is None:  # pragma: no cover
            error('Filtering columns failed, column names are missing for '
                  f'{self._path}')
            return iterator

        # Skip first skip_columns columns
        keys = iterator.fieldnames[self._skip_columns:]
        debug(f'Filtering columns: {keys}')
        for row in iterator:
            yield dict((k, row[k]) for k in keys)

    def _trim_result(self, result: Dict) -> Dict:
        """
        Trims the CSV row values depending on the CSVW trimming mode:
            - START_AND_END: both sides are trimmed
            - START: beginning is trimmed
            - END: end is trimmed
            - NONE: trimming disabled
        """
        # Trimming disabled, return
        if self._trim_mode == CSVWTrimMode.NONE:
            return result

        # Trim based on CSVW trimming mode
        k: str
        v: str
        for k, v in result.items():
            if self._trim_mode == CSVWTrimMode.START:
                result[k] = v.lstrip()
            elif self._trim_mode == CSVWTrimMode.END:
                result[k] = v.rstrip()
            else:
                result[k] = v.strip()
        return result

    def _replace_null_values(self, result: Dict) -> Dict:
        """
        Checks if the CSV values are NULL and replaces them with None if
        needed.
        """
        for column, value in result.items():
            # Try to use provided null values, if column is missing, fallback
            if value.strip() == \
                    self._null_values.get(column, DEFAULT_NULL_VALUE).strip():
                result[column] = None
        debug(f'Replaced null values: {result}')
        return result

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.CSV.
        """
        return MIMEType.CSV
