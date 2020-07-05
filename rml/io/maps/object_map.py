from rdflib.term import URIRef, Literal, Identifier
from jsonpath_ng import parse
from typing import Union, Dict
from lxml.etree import Element

from . import TermMap, TermType
from rml.io.sources import MIMEType


class ObjectMap(TermMap):
    def __init__(self, term: str, term_type: TermType,
                 reference_formulation: MIMEType, is_iri: bool = True) -> None:
        super().__init__(term, term_type, reference_formulation)
        self._is_iri = is_iri

    def resolve(self, data: Union[Element, Dict]) -> Identifier:
        if self._term_type == TermType.TEMPLATE:
            if self._is_iri:
                return URIRef(super()._resolve_template(data))
            # If no IRI, return a Literal
            return Literal(super()._resolve_template(data))
        elif self._term_type == TermType.REFERENCE:
            if self._is_iri:
                return URIRef(super()._resolve_reference(self._term, data))
            # If no IRI, return a Literal
            return Literal(super()._resolve_reference(self._term, data))
        elif self._term_type == TermType.CONSTANT:
            return URIRef(self._term)
        else:
            raise ValueError(f'Unknown term type: {self._term_type}')
