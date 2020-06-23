from . import SubjectMap, PredicateMap, ObjectMap
from ..sources import LogicalSource

class TriplesMap:
    def __init__(self, logical_source: LogicalSource, subject_map: SubjectMap,
                 predicate_map: PredicateMap, object_map: ObjectMap):
        self._logical_source = logical_source
        self._subject_map = subject_map
        self._predicate_object_map = predicate_object_map

    def __iter__(self) -> iter:
        """
        Every Triples Map is a Python iterator
        """
        return self

    def __next__(self) -> tuple:
        """
        Generates a triple according to the given Subject Map, Predicate Map
        and Object Map.
        """
        subj = self._subject_map.resolve()
        pred = self._predicate_map.resolve()
        obj = self._object_map.resolve()
        return (subj, pred, obj)
