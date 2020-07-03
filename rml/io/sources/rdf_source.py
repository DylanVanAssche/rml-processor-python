from rdflib import ConjunctiveGraph, Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from typing import Dict, Iterator

from . import LogicalSource, MIMEType

class RDFLogicalSource(LogicalSource):
    def __init__(self, path: str, query: str, format: MIMEType) -> None:
        """
        An RDF Logical Source to iterate over triples.
        The RML reference formulation is not used for row-based iterators.
        The query is a SPARQL query to select triples.
        """
        super().__init__()
        self._path: str = path
        self._query: Query = prepareQuery(query)
        self._format: MIMEType = format
        self._graph: Graph

        # Create a context-aware graph for specific formats
        # https://github.com/RDFLib/rdflib-jsonld/issues/40 JSON-LD requires
        # ConjunctiveGraph to parse @graph triples
        f: str = self._format.value
        if f == MIMEType.NQUADS.value or \
           f == MIMEType.JSON_LD.value or \
           f == MIMEType.TRIG.value or \
           f == MIMEType.TRIX.value:
               self._graph = ConjunctiveGraph()
        # Create a normal graph for other RDF formats
        elif f == MIMEType.RDF_XML.value or \
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
        except FileNotFoundError:
            raise FileNotFoundError(f'Unable to open {self._path}')
        except Exception:
            raise ValueError(f'Unable to parse {self._path}')

        # Execute SPARQL query and return results iterator
        self._iterator: Iterator = iter(self._graph.query(self._query))

    def __next__(self) -> Dict:
        """
        Returns a row from the RDF iterator.
        raises StopIteration when exhausted.
        """
        record: Dict = next(self._iterator).asdict()
        return record

    @property
    def graph(self) -> Graph:
        """
        Returns the knowledge graph.
        """
        return self._graph

