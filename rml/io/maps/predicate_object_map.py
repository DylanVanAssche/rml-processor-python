from typing import Union
from rdflib.term import Identifier

from ..maps import PredicateMap, ObjectMap

class PredicateObjectMap:
    def __init__(self, predicate_map: PredicateMap,
                 object_map: ObjectMap) -> None:
        self._predicate_map = predicate_map
        self._object_map = object_map

    def resolve(self, data) -> Union[Identifier, Identifier]:
        """
        Resolves the predicate and object maps with the given data record.
        """
        pred = self._predicate_map.resolve(data)
        obj = self._object_map.resolve(data)
        return pred, obj
