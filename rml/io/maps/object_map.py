from rdflib import Namespace
from rdflib.term import URIRef, Literal, Identifier
from jsonpath_ng import parse
from typing import Union, Dict, Optional
from lxml.etree import Element

from . import TermMap, TermType
from rml.io.sources import MIMEType
from rml.namespace import XSD


class ObjectMap(TermMap):
    def __init__(self, term: str, term_type: TermType,
                 reference_formulation: MIMEType, language: str = None,
                 datatype: Namespace = None, is_iri: bool = True) -> None:
        """
        Creates an ObjectMap
        """
        super().__init__(term, term_type, reference_formulation)
        self._language: Optional[str] = language
        self._datatype: Optional[Namespace] = datatype
        self._is_iri: bool = is_iri

    def resolve(self, data: Union[Element, Dict]) -> Identifier:
        """
        Resolves an object into an RDF Identifier.
        """
        # RML template
        resolved_term: str
        if self._term_type == TermType.TEMPLATE:
            resolved_term = super()._resolve_template(data)
            if self._is_iri:
                return URIRef(resolved_term)
            return self._handle_literal(resolved_term)
        # RML reference
        elif self._term_type == TermType.REFERENCE:
            resolved_term = super()._resolve_reference(self._term, data)
            if self._is_iri:
                return URIRef(resolved_term)
            # If no IRI, return a Literal
            return self._handle_literal(resolved_term)
        elif self._term_type == TermType.CONSTANT:
            return URIRef(self._term)
        # Term type unsupported for ObjectMap
        else:
            raise ValueError(f'Unknown term type: {self._term_type}')

    def _handle_literal(self, term: str) -> Literal:
        """
        Handle Literal's language tags and datatypes.
        """
        # If no IRI, return a Literal
        # Language tag or data type specified
        if self._language is not None or self._datatype is not None:
            try:
                return Literal(term,
                               lang = self._language,
                               datatype = self._datatype)
            # Invalid language tag, invalid datatype or both specified
            except TypeError:
                raise TypeError('Literals can only have a language tag or '
                                'a datatype, not both')
            except Exception:
                raise ValueError(f'Invalid language tag: {self._language}')
        else:
            return Literal(term)
