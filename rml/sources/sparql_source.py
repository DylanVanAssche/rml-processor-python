from SPARQLWrapper import SPARQLWrapper, JSON
from jsonpath_ng import parse
from requests import get, HTTPError

from . import LogicalSource

class SPARQLLogicalSource(LogicalSource):
    def __init__(self, reference_formulation: str, endpoint: str, query: str):
        """
        An SPARQL Logical Source to iterate over RDF data.
        The RML reference formulation is used to select the JSON results.
        """
        super().__init__(reference_formulation)
        self._query = query
        try:
            get(endpoint).raise_for_status()
        except HTTPError:
            raise FileNotFoundError
        self._engine = SPARQLWrapper(endpoint, returnFormat=JSON)
        self._engine.setQuery(self._query)
        try:
            self._iterator = parse(self._reference_formulation)
        except:
            raise ValueError('Invalid JSONPath expression')

        results = self._engine.query().convert()['results']['bindings']
        self._iterator = iter(self._iterator.find(results))

    def __next__(self):
        """
        Returns a result from the SPARQL iterator.
        raises StopIteration when exhausted.
        """
        return next(self._iterator).value
