from logging import debug, critical, getLogger, DEBUG
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.reflection import Inspector
from typing import Dict

from rml.io.sources import LogicalSource, MIMEType


class SQLLogicalSource(LogicalSource):
    def __init__(self, jdbc: str, query: str = None, table_name: str = None):
        """
        An SQL Logical Source to iterate over RDB data.
        The RML iterator is not used for row-based iterators.
        """
        super().__init__()
        self._jdbc = jdbc
        self._query = query
        debug(f'JDBC: {self._jdbc}')
        debug(f'Query: {self._query}')

        # Connect to database
        try:
            # Pass through logging if level is DEBUG
            self._engine = create_engine(self._jdbc,
                                         echo=getLogger().isEnabledFor(DEBUG))
            self._connection = self._engine.connect()
        except OperationalError as e:
            msg = f'Cannot connect to database {self._jdbc}: {e}'
            critical(msg)
            raise FileNotFoundError(msg)

        # Execute SQL query on database
        try:
            self._iterator = self._connection.execute(self._query)
        except OperationalError as e:
            self._connection.close()
            msg = f'Connection to database lost {self._jdbc}: {e}'
            critical(msg)
            raise ValueError(msg)

        debug('Source initialization complete')

    def __next__(self) -> Dict:
        """
        Returns a result from the SQL iterator.
        raises StopIteration when exhausted.
        """
        try:
            result = dict(next(self._iterator))
            debug('Result: {result}')
            return result
        except StopIteration:
            self._connection.close()
            debug('SQL connection closed')
            raise StopIteration

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.SQL.
        """
        return MIMEType.SQL
