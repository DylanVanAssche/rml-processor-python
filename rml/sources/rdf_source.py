from rdflib import Graph
from rdflib.util import guess_format
from rdflib.plugins.sparql import prepareQuery
from xml.sax import SAXParseException

from . import LogicalSource

class RDFLogicalSource(LogicalSource):
    def __init__(self, path: str, query: str):
        """
        An RDF Logical Source to iterate over triples.
        The RML reference formulation is not used for row-based iterators.
        The query is a SPARQL query to select triples.
        """
        super().__init__()
        self._path = path
        self._query = prepareQuery(query)
        self._graph = Graph()
        self._format = guess_format(self._path)
        try:
            self._graph.parse(path, format=self._format)
        except SAXParseException:
            raise FileNotFoundError(f'Unable to open {self._path}')
        self._iterator = self._graph.query(self._query)
        self._iterator = iter(self._iterator)

    def __next__(self):
        """
        Returns a row from the RDF iterator.
        raises StopIteration when exhausted.
        """
        return next(self._iterator)
