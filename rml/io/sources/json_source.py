import json
from logging import debug, critical
from jsonpath_ng import parse
from jsonpath_ng.parser import JsonPathParser
from typing import Iterator, Dict

from rml.io.sources import LogicalSource, MIMEType


class JSONLogicalSource(LogicalSource):
    def __init__(self, reference_formulation: str, path: str):
        """
        A JSONPath Logical Source to iterate over JSON data.
        """
        super().__init__(reference_formulation)
        try:
            json_path: JsonPathParser = parse(self._reference_formulation)
        except Exception as e:
            msg = f'Invalid JSONPath expression: {e}'
            critical(msg)
            raise ValueError(msg)
        self._path: str = path
        self._data: Dict = {}
        debug('Path: {self._path}')

        # Read JSON file
        with open(self._path) as f:
            self._data = json.load(f)
            self._iterator: Iterator = iter(json_path.find(self._data))
        debug('Source initialization complete')

    def __next__(self) -> Dict:
        """
        Returns a result from the JSONPath iterator.
        """
        result: Dict = next(self._iterator).value
        debug(f'Iterator: {result}')
        return result

    @property
    def mime_type(self) -> MIMEType:
        """
        Return MIMEType.JSON
        """
        return MIMEType.JSON
