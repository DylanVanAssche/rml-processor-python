from csv import DictReader, Sniffer

from . import LogicalSource

BYTES_TO_SNIFF=1024

class CSVLogicalSource(LogicalSource):
    def __init__(self, path):
        """
        A CSV Logical Source to iterate over CSV data.
        The RML reference formulation is not used for row-based iterators.
        """
        super().__init__()
        self._path = path
        self._file = open(self._path)
        with open(self._path) as csvfile:
            sniffer = Sniffer()
            if not sniffer.has_header(csvfile.read(BYTES_TO_SNIFF)):
                raise ValueError('CSV file requires a header')
        self._iterator = DictReader(self._file)

    def __next__(self):
        """
        Returns a row from the CSV iterator.
        raises StopIteration when exhausted.
        """
        try:
            return next(self._iterator)
        except StopIteration:
            self._file.close()
            raise StopIteration
