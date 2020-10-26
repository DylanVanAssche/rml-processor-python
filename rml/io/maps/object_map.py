from logging import debug, critical
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
                 mime_type: MIMEType, language: str = None,
                 datatype: Namespace = None, is_iri: bool = False) -> None:
        """
        Creates an ObjectMap
        """
        super().__init__(term, term_type, mime_type)
        self._language: Optional[str] = language
        self._datatype: Optional[Namespace] = datatype
        self._is_iri: bool = is_iri
        self._rr_term_type = term_type
        debug(f'Language: {self._language}')
        debug(f'Datatype: {self._datatype}')
        debug(f'Is IRI?: {self._is_iri}')
        debug('ObjectMap initialization complete')

    def resolve(self, data: Union[Element, Dict]) -> Identifier:
        """
        Resolves an object into an RDF Identifier.
        """
        # R2RML template
        resolved_term: Optional[str]
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
            return self._handle_literal(resolved_term)
        # R2RML constant
        elif self._term_type == TermType.CONSTANT:
            if self._is_iri:
                return URIRef(self._term)
            return self._handle_literal(self._term)
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
            debug('Language (self._language) or datatype (self._datatype) '
                  'detected')
            if self._datatype == XSD.dateTime:
                term = term.replace(' ', 'T')
                debug('Replaced \'space\' with \'T\' for XSD.dateTime')
            try:
                return Literal(term,
                               lang=self._language,
                               datatype=self._datatype)
            # Both specified
            except TypeError:
                msg = 'Literals can only have a language tag or a '
                'datatype, not both!'
                critical(msg)
                raise TypeError(msg)
            # Invalid language tag
            except Exception:
                msg = f'Invalid language tag: {self._language}'
                critical(msg)
                raise ValueError(msg)
        else:
            return Literal(term)
