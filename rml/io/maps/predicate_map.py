from logging import debug, critical
from rdflib.term import URIRef, Identifier
from jsonpath_ng import parse
from typing import Union, Dict
from lxml.etree import Element

from . import TermMap, ReferenceType
from rml.io.sources import MIMEType


class PredicateMap(TermMap):
    def __init__(self, term: str, reference_type: ReferenceType,
                 mime_type: MIMEType) -> None:
        """
        Creates a PredicateMap.
        """
        super().__init__(term, reference_type, mime_type)
        debug('PredicateMap initialization complete')

    def resolve(self, data: Union[Element, Dict]) -> Identifier:
        """
        Resolves a predicate into an RDF Identifier.
        """
        if self._reference_type == ReferenceType.TEMPLATE:
            return URIRef(super()._resolve_template(data))
        elif self._reference_type == ReferenceType.REFERENCE:
            return URIRef(super()._resolve_reference(self._term, data))
        elif self._reference_type == ReferenceType.CONSTANT:
            return URIRef(self._term)
        else:
            msg = f'Unknown term type: {self._reference_type}'
            critical(msg)
            raise ValueError(msg)
