import json
from jsonpath_ng import parse

from . import LogicalSource

class JSONLogicalSource(LogicalSource):
    def __init__(self, reference_formulation, path):
        """
        A JSONPath Logical Source to iterate over JSON data.
        """
        super().__init__(reference_formulation)
        self._iterator = parse(self._reference_formulation)
        self._path = path
        self._data = {}

        # Read JSON file
        with open(self._path) as f:
            self._data = json.load(f)

    def __next__(self):
        """
        Returns an iterator from the JSONPath expression.
        """
        return self._iterator.find(self._data)
