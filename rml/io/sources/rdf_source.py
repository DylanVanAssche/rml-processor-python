from rdflib import ConjunctiveGraph, Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from typing import Dict, Iterator

from rml.io.sources import LogicalSource, MIMEType


class RDFLogicalSource(LogicalSource):
    def __init__(self, path: str, query: str, mime_type: MIMEType) -> None:
        """
        An RDF Logical Source to iterate over triples.
        The RML reference formulation is not used for row-based iterators.
        The query is a SPARQL query to select triples.
        """
        super().__init__()
        self._path: str = path
        self._query: Query = prepareQuery(query)
        self._mime_type: MIMEType = mime_type
        self._graph: Graph

        # Create a context-aware graph for specific mime_types
        # https://github.com/RDFLib/rdflib-jsonld/issues/40 JSON-LD requires
        # ConjunctiveGraph to parse @graph triples
        f: str = self._mime_type.value
        if f == MIMEType.NQUADS.value or \
                f == MIMEType.JSON_LD.value or \
                f == MIMEType.TRIG.value or \
                f == MIMEType.TRIX.value:
            self._graph = ConjunctiveGraph()
        # Create a normal graph for other RDF mime_types
        elif f == MIMEType.RDF_XML.value or \
                f == MIMEType.N3.value or \
                f == MIMEType.TURTLE.value or \
                f == MIMEType.NTRIPLES.value:
            self._graph = Graph()
        # Raise ValueError when MIME type is not supported
        else:
            raise ValueError('Unknown RDF MIME type: {self._mime_type}')

        # Parse RDF data
        try:
            print(self._mime_type)
            print(f'MIME type: {f}')
            self._graph.parse(path, format=f)
        except FileNotFoundError:
            raise FileNotFoundError(f'Unable to open {self._path}')
        except Exception as e:
            raise ValueError(f'Unable to parse {self._path}, exception: {e}')

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

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns the provided MIME type.
        """
        return self._mime_type
