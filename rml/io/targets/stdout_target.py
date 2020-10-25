from rml.io.targets import LogicalTarget
from typing import List, Tuple
from rdflib.term import URIRef, Identifier

from rml.io.maps.triples_map import TriplesMap


class StdoutLogicalTarget(LogicalTarget):
    def __init__(self, triples_maps: List[TriplesMap]) -> None:
        """
        Creates a Logical Target with stdout as target.
        """
        super().__init__(triples_maps)
        self._number_of_triples_maps = len(self._triples_maps)

    def _add_to_target(self, triple: Tuple[URIRef, URIRef, Identifier,
                                           URIRef]) -> None:
        """
        Adds a single triple to stdout.
        """
        print('<%s> <%s> <%s> .' % triple[0:3])
