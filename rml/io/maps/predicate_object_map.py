from typing import Union, Dict, Optional
from lxml.etree import Element
from rdflib.term import Identifier, URIRef

from rml.io.maps import PredicateMap, ObjectMap


class PredicateObjectMap:
    def __init__(self, predicate_map: PredicateMap, object_map: ObjectMap,
                 rr_graph: Optional[URIRef] = None) -> None:
        """
        Creates a PredicateObjectMap
        """
        self._predicate_map = predicate_map
        self._object_map = object_map
        self._rr_graph = rr_graph

    def resolve(self, data: Union[Element, Dict]) \
            -> Union[Identifier, Identifier, URIRef]:
        """
        Resolves the predicate and object maps with the given data record.
        """
        pred = self._predicate_map.resolve(data)
        obj = self._object_map.resolve(data)
        return pred, obj, self._rr_graph
