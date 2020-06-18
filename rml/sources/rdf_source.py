from rdflib import ConjunctiveGraph, Graph
from rdflib.plugins.sparql import prepareQuery
from xml.sax import SAXParseException

from . import LogicalSource, MIMEType

class RDFLogicalSource(LogicalSource):
    def __init__(self, path: str, query: str, format: MIMEType):
        """
        An RDF Logical Source to iterate over triples.
        The RML reference formulation is not used for row-based iterators.
        The query is a SPARQL query to select triples.
        """
        super().__init__()
        self._path = path
        self._query = prepareQuery(query)
        self._format = format

        # Create a context-aware graph for specific formats
        f = self._format.value
        if f == MIMEType.NQUADS.value or \
           f == MIMEType.TRIG.value or \
           f == MIMEType.TRIX.value:
            self._graph = ConjunctiveGraph()
        # Create a normal graph for other RDF formats
        elif f == MIMEType.RDF_XML.value or \
             f == MIMEType.JSON_LD.value or \
             f == MIMEType.N3.value or \
             f == MIMEType.TURTLE.value or \
             f == MIMEType.NTRIPLES.value:
            self._graph = Graph()
        # Raise ValueError when MIME type is not supported
        else:
            raise ValueError('Unknown RDF MIME type: {self._format}')

        # Parse RDF data
        try:
            self._graph.parse(path, format=f)
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
