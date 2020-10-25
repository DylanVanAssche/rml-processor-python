from typing import List, Iterator, Tuple
from rdflib.term import URIRef, Identifier

from . import SubjectMap, PredicateObjectMap
from rml.io.sources import LogicalSource
from rml.namespace import RDF


class TriplesMap:
    def __init__(self, logical_source: LogicalSource, subject_map: SubjectMap,
                 predicate_object_maps: List[PredicateObjectMap]) -> None:
        self._logical_source = logical_source
        self._subject_map = subject_map
        self._predicate_object_maps = predicate_object_maps

    def __iter__(self) \
            -> Iterator[List[Tuple[URIRef, URIRef, Identifier, URIRef]]]:
        """
        Every Triples Map is a Python iterator
        """
        return self

    def __next__(self) -> List[Tuple[URIRef, URIRef, Identifier, URIRef]]:
        """
        Generates all triples of this TriplesMap according to the given Subject
        Map, Predicate Map and Object Map for a single data record.
        """
        # Get data record
        data = next(self._logical_source)

        # Generate subject
        try:
            subj, rr_class, subj_graph = self._subject_map.resolve(data)
        except ResourceWarning:
            print('Unable to resolve SubjectMap, missing data')
            return []

        triples: List[Tuple[URIRef, URIRef, Identifier, URIRef]] = []

        # Generate predicate and objects
        for po in self._predicate_object_maps:
            try:
                pred, obj, po_graph = po.resolve(data)
            except ResourceWarning:
                print('Unable to resolve PredicateObjectMap, missing data')
                continue
            t = (subj, pred, obj, po_graph)
            triples.append(t)

        return triples
