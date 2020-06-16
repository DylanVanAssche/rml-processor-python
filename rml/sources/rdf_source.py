from enum import Enum
from rdflib import ConjunctiveGraph, Graph
from rdflib.plugins.sparql import prepareQuery
from xml.sax import SAXParseException

from . import LogicalSource

class RDFFormat(Enum):
    XML = 'xml'
    JSON_LD = 'json-ld'
    TRIX = 'trix'
    TRIG = 'trig'
    N3 = 'n3'
    NQUADS = 'nquads'
    TURTLE = 'turtle'
    NTRIPLES = 'nt'

class RDFLogicalSource(LogicalSource):
    def __init__(self, path: str, query: str, format: RDFFormat):
        """
        An RDF Logical Source to iterate over triples.
        The RML reference formulation is not used for row-based iterators.
        The query is a SPARQL query to select triples.
        """
        super().__init__()
        self._path = path
        self._query = prepareQuery(query)
        self._format = format.value

        # Create a context-aware graph for specifc formats
        if self._format == RDFFormat.NQUADS.value or \
           self._format == RDFFormat.TRIG.value or \
           self._format ==RDFFormat.TRIX.value:
            self._graph = ConjunctiveGraph()
        else:
            self._graph = Graph()

        # Parse RDF data
        try:
            self._graph.parse(path, format=self._format)
        except SAXParseException:
            raise FileNotFoundError(f'Unable to open {self._path}')

        # Execute SPARQL query and return results iterator
        self._iterator = self._graph.query(self._query)
        self._iterator = iter(self._iterator)

    def __next__(self):
        """
        Returns a row from the RDF iterator.
        raises StopIteration when exhausted.
        """
        return next(self._iterator)
