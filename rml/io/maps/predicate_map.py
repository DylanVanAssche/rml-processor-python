from logging import debug, critical
from rdflib.term import URIRef, Identifier
from jsonpath_ng import parse
from typing import Union, Dict
from lxml.etree import Element

from . import TermMap, TermType
from rml.io.sources import MIMEType


class PredicateMap(TermMap):
    def __init__(self, term: str, term_type: TermType,
                 mime_type: MIMEType) -> None:
        """
        Creates a PredicateMap.
        """
        super().__init__(term, term_type, mime_type)
        debug('PredicateMap initialization complete')

    def resolve(self, data: Union[Element, Dict]) -> Identifier:
        """
        Resolves a predicate into an RDF Identifier.
        """
        if self._term_type == TermType.TEMPLATE:
            return URIRef(super()._resolve_template(data))
        elif self._term_type == TermType.REFERENCE:
            return URIRef(super()._resolve_reference(self._term, data))
        elif self._term_type == TermType.CONSTANT:
            return URIRef(self._term)
        else:
            msg = f'Unknown term type: {self._term_type}'
            critical(msg)
            raise ValueError(msg)
