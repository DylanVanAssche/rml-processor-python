from abc import ABC, abstractmethod
from typing import List, Iterator, Tuple
from rdflib.term import URIRef, Identifier

from rml.io.maps.triples_map import TriplesMap


class LogicalTarget(ABC):
    def __init__(self, triples_maps: List[TriplesMap]) -> None:
        """
        Creates a Logical Target.
        """
        self._triples_maps: List[TriplesMap] = triples_maps
        self._number_of_triples_maps = len(self._triples_maps)

    def write(self) -> None:
        """
        Write a single record of triples to target.
        """
        exhausted_counter = 0
        for tm in self._triples_maps:
            try:
                triples = next(tm)
                for t in triples:
                    self._add_to_target(t)
            except StopIteration:
                exhausted_counter = exhausted_counter + 1
                # All exhausted? Raise StopIteration
                if exhausted_counter == self._number_of_triples_maps:
                    raise StopIteration

    def write_all(self) -> None:
        """
        Write all records of triples to target.
        """
        while True:
            try:
                self.write()
            except StopIteration:
                return

    @abstractmethod
    def _add_to_target(self,
                       triple: Tuple[URIRef, URIRef, Identifier]) -> None:
        """
        Adds a single triple to target.
        """


# Expose classes at module level
from rml.io.targets.stdout_target import StdoutLogicalTarget  # nopep8
from rml.io.targets.file_target import FileLogicalTarget  # nopep8
