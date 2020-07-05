from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from typing import Dict

from . import LogicalSource


class SQLLogicalSource(LogicalSource):
    def __init__(self, jdbc: str, query: str):
        """
        An SQL Logical Source to iterate over RDB data.
        The RML reference formulation is not used for row-based iterators.
        """
        super().__init__()
        self._jdbc = jdbc
        self._query = query
        try:
            # Pass through logging
            self._engine = create_engine(self._jdbc, echo=True)
            self._connection = self._engine.connect()
        except OperationalError:
            raise FileNotFoundError

        try:
            self._iterator = self._connection.execute(self._query)
        except OperationalError:
            self._connection.close()
            raise ValueError

    def __next__(self) -> Dict:
        """
        Returns a row from the SQL iterator.
        raises StopIteration when exhausted.
        """
        try:
            row = dict(next(self._iterator))
            return {k.lower(): v for k, v in row.items()}
        except StopIteration:
            self._connection.close()
            raise StopIteration
