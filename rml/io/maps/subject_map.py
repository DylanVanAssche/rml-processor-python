from logging import debug, critical
from rdflib.term import URIRef, Identifier, BNode
from jsonpath_ng import parse
from typing import Union, Dict, Tuple, List, Optional
from lxml.etree import Element

from rml.namespace import R2RML
from . import TermMap, ReferenceType
from rml.io.sources import MIMEType


class SubjectMap(TermMap):
    def __init__(self, term: str, reference_type: ReferenceType,
                 mime_type: MIMEType, rr_reference_type: URIRef,
                 rr_class: Optional[List[URIRef]] = [],
                 rr_graph: Optional[URIRef] = None) -> None:
        """
        Creates a SubjectMap.
        """
        super().__init__(term, reference_type, mime_type)
        self._rr_reference_type = rr_reference_type
        self._rr_class = rr_class
        self._rr_graph = rr_graph
        debug('Term type: {self._rr_reference_type}')
        debug('Class: {self._rr_class}')
        debug('Named graph: {self._rr_graph}')
        debug('SubjectMap initialization complete')

    def resolve(self, data: Union[Element, Dict]) \
            -> Tuple[Identifier, URIRef, URIRef]:
        """
        Resolves a subject into an RDF Identifier.
        """
        if self._reference_type == ReferenceType.TEMPLATE:
            value = super()._resolve_template(data)
            if self._rr_reference_type == R2RML.BlankNode:
                return BNode(value=value), self._rr_class, self._rr_graph
            return URIRef(value), self._rr_class, self._rr_graph
        elif self._reference_type == ReferenceType.REFERENCE:
            value = super()._resolve_reference(self._term, data)
            if self._rr_reference_type == R2RML.BlankNode:
                return BNode(value=value), self._rr_class, self._rr_graph
            return URIRef(value), self._rr_class, self._rr_graph
        elif self._reference_type == ReferenceType.CONSTANT:
            if self._rr_reference_type == R2RML.BlankNode:
                return BNode(value=self._term), self._rr_class, self._rr_graph
            return URIRef(self._term), self._rr_class, self._rr_graph
        else:
            msg = f'Unknown term type: {self._reference_type}'
            critical(msg)
            raise ValueError(msg)
