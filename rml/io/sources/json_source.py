import json
from jsonpath_ng import parse
from jsonpath_ng.parser import JsonPathParser
from typing import Iterator, Dict

from . import LogicalSource


class JSONLogicalSource(LogicalSource):
    def __init__(self, reference_formulation: str, path: str):
        """
        A JSONPath Logical Source to iterate over JSON data.
        """
        super().__init__(reference_formulation)
        try:
            json_path: JsonPathParser = parse(self._reference_formulation)
        except Exception:
            raise ValueError('Invalid JSONPath expression')
        self._path: str = path
        self._data: Dict = {}

        # Read JSON file
        with open(self._path) as f:
            self._data = json.load(f)
            self._iterator: Iterator = iter(json_path.find(self._data))

    def __next__(self) -> Dict:
        """
        Returns an iterator from the JSONPath expression.
        """
        record: Dict = next(self._iterator).value
        return record
