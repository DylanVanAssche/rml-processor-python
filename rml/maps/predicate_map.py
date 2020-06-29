from uritemplate import URITemplate
from rdflib.term import URIRef, Identifier
from jsonpath_ng import parse

from . import TermMap, TermType
from ..io.sources import MIMEType

class PredicateMap(TermMap):
    def __init__(self, term: str, term_type: TermType,
                 reference_formulation: MIMEType) -> None:
        super().__init__(term, term_type, reference_formulation)

    def resolve(self, data) -> Identifier:
        if self._term_type == TermType.CONSTANT:
            return URIRef(self._term)
        else:
            raise ValueError(f'Unknown term type: {self._term_type}')
