from csv import DictReader

from . import LogicalSource

class CSVLogicalSource(LogicalSource):
    def __init__(self, path):
        """
        A CSV Logical Source to iterate over CSV data.
        The RML reference formulation is not used for row-based iterators.
        """
        super().__init__()
        self._path = path
        self._file = open(self._path)
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

    def __del__(self):
        """
        Clean up CSV file descriptor
        """
        self._file.close()
