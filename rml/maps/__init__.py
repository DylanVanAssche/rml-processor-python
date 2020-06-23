from abc import ABC, abstractmethod
from enum import Enum
from rdflib.term import Identifier

from ..namespace import R2RML, RML
from ..sources import MIMEType

class TermType(Enum):
    CONSTANT = R2RML.constant
    TEMPLATE = R2RML.template
    REFERENCE = RML.reference
    UNKNOWN = 'UNKNOWN' # Used for unittests

class TermMap(ABC):
    def __init__(self, term: str, term_type: TermType,
                 reference_formulation: MIMEType):
        """
        R2RML/RML Term Map
        """
        self._term = term
        self._term_type = term_type
        self._reference_formulation = reference_formulation

    @abstractmethod
    def resolve(self, data) -> Identifier:
        """
        Resolve the given term as RDF IRI or RDF Literal .
        """

# Expose classes at module level
from rml.maps.subject_map import SubjectMap
