from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.reflection import Inspector
from typing import Dict

from rml.io.sources import LogicalSource, MIMEType


class SQLLogicalSource(LogicalSource):
    def __init__(self, jdbc: str, query: str = None, table_name: str = None):
        """
        An SQL Logical Source to iterate over RDB data.
        The RML reference formulation is not used for row-based iterators.
        """
        super().__init__()
        self._jdbc = jdbc
        self._query = query

        # Connect to database
        try:
            # Pass through logging
            self._engine = create_engine(self._jdbc, echo=True)
            self._connection = self._engine.connect()
        except OperationalError as e:
            raise FileNotFoundError(f'Cannot connect to database {self._jdbc}:'
                                    f' {e}')

        # Execute SQL query on database
        try:
            self._iterator = self._connection.execute(self._query)
        except OperationalError:
            self._connection.close()
            raise ValueError(f'Connection to database lost: {self._jdbc}')

    def __next__(self) -> Dict:
        """
        Returns a row from the SQL iterator.
        raises StopIteration when exhausted.
        """
        try:
            row = dict(next(self._iterator))
            return row
        except StopIteration:
            self._connection.close()
            raise StopIteration

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.SQL.
        """
        return MIMEType.SQL
