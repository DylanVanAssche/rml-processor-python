from logging import debug, warning, critical
from typing import Iterator, IO, Dict, Sequence, Optional
from csv import DictReader, Sniffer, Error

from rml.io.sources import LogicalSource, MIMEType

BYTES_TO_SNIFF = 1024
DEFAULT_DELIMITER = ','


class CSVLogicalSource(LogicalSource):
    def __init__(self, path: str, delimiter: str = ','):
        """
        A CSV Logical Source to iterate over CSV data.
        The RML iterator is not used for row-based iterators.
        """
        super().__init__()
        self._path: str = path
        self._delimiter: str = delimiter
        debug(f'Path: {self._path}')
        debug(f'Delimiter: {self._delimiter}')

        with open(self._path) as f:
            # Check if the CSV file contains a header
            sniffer: Sniffer = Sniffer()
            try:
                if not sniffer.has_header(f.read(BYTES_TO_SNIFF)):
                    msg = 'CSV file requires a header'
                    critical(msg)
                    raise ValueError(msg)
            # Sniffer raises Error when delimiter cannot be determined
            except Error as e:  # pragma: no cover
                warning('Unable to determine delimiter, falling back to '
                        f'default ({DEFAULT_DELIMITER})')

        # Create CSV file iterator
        self._file: IO = open(self._path)
        self._iterator: Iterator = DictReader(self._file,
                                              delimiter=self._delimiter)
        debug('Source initialization complete')

    def __next__(self) -> Dict:
        """
        Returns a row from the CSV iterator.
        raises StopIteration when exhausted.
        """
        try:
            result: Dict = next(self._iterator)
            debug(f'Iterator: {result}')
            return result
        # Iterator exhausted
        except StopIteration:
            self._file.close()
            debug('File closed')
            raise StopIteration

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.CSV.
        """
        return MIMEType.CSV
