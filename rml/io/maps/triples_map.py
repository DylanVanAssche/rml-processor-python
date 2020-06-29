from typing import List

from . import SubjectMap, PredicateObjectMap
from rml.io.sources import LogicalSource

class TriplesMap:
    def __init__(self, logical_source: LogicalSource, subject_map: SubjectMap,
            predicate_object_maps: List[PredicateObjectMap]) -> None:
        self._logical_source = logical_source
        self._subject_map = subject_map
        self._predicate_object_maps = predicate_object_maps

    def __iter__(self) -> iter:
        """
        Every Triples Map is a Python iterator
        """
        return self

    def __next__(self) -> List[tuple]:
        """
        Generates all triples of this TriplesMap according to the given Subject 
        Map, Predicate Map and Object Map for a single data record.
        """
        # Get data record
        data = next(self._logical_source)

        # Generate subject
        subj = self._subject_map.resolve(data)

        # Generate predicate and objects
        triples = []
        for po in self._predicate_object_maps:
            pred, obj = po.resolve(data)
            t = (subj, pred, obj)
            triples.append(t)

        return triples
