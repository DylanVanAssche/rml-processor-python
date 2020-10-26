from logging import debug
from typing import List, Tuple, TextIO
from rdflib.term import URIRef, Identifier
from rdflib import Graph

from rml.io.targets import LogicalTarget
from rml.io.maps.triples_map import TriplesMap
from rml.io.sources import MIMEType


class FileLogicalTarget(LogicalTarget):
    def __init__(self, triples_maps: List[TriplesMap], path: str,
                 format: MIMEType) -> None:
        """
        Creates a Logical Target with stdout as target.
        """
        super().__init__(triples_maps)
        self._path: str = path
        self._graph = Graph()
        self._format: MIMEType = format
        debug('Path: {self._path}')
        debug('Serialization format: {self._format}')
        debug('Target initialization complete')

    def write(self) -> None:
        """
        Write a single record of triples to the file.
        """
        try:
            super().write()
        except StopIteration:
            debug('Wrote single record')
            raise StopIteration

    def _add_to_target(self, triple: Tuple[URIRef, URIRef, Identifier,
                                           URIRef]) -> None:
        """
        Adds a single triple to the file.
        """
        self._graph.add(triple[0:3])

        # When https://github.com/RDFLib/rdflib/issues/283 is fixed, use a
        # streaming serializer to avoid writing the whole file over and over
        # again.
        self._graph.serialize(destination=self._path,
                              format=self._format.value)
        debug(f'Serialized to {self._path}')
