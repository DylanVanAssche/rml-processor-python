from typing import Iterator, IO, Dict
from csv import DictReader, Sniffer

from rml.io.sources import LogicalSource, MIMEType

BYTES_TO_SNIFF = 1024


class CSVLogicalSource(LogicalSource):
    def __init__(self, path: str, delimiter: str = ','):
        """
        A CSV Logical Source to iterate over CSV data.
        The RML reference formulation is not used for row-based iterators.
        """
        super().__init__()
        self._path: str = path
        self._delimiter: str = delimiter

        with open(self._path) as f:
            # Check if the CSV file contains a header
            sniffer: Sniffer = Sniffer()
            if not sniffer.has_header(f.read(BYTES_TO_SNIFF)):
                raise ValueError('CSV file requires a header')

        # Create CSV file iterator
        self._file: IO = open(self._path)
        self._iterator: Iterator = DictReader(self._file,
                                              delimiter=self._delimiter)

    def __next__(self) -> Dict:
        """
        Returns a row from the CSV iterator.
        raises StopIteration when exhausted.
        """
        try:
            return next(self._iterator)
        except StopIteration:
            self._file.close()
            raise StopIteration

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.CSV.
        """
        return MIMEType.CSV
