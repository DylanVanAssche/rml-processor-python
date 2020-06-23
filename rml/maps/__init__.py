from abc import ABC, abstractmethod
from enum import Enum
from rdflib.term import Identifier
from uritemplate import URITemplate
from jsonpath_ng import parse

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

    def _resolve_template(self, data) -> str:
        # term.expand() is broken when an XPath expression is used
        # https://github.com/python-hyper/uritemplate/issues/56
        ###########################################################
        #term = URITemplate(self._term)
        #variables = term.variables
        #resolved_variables = {}

        ## Resolve each variable in template
        #if variables:
        #    for var in variables:
        #        var = str(var)
        #        resolved_var = self._resolve_reference(var, data)
        #        resolved_variables[var] = resolved_var
        #    print(resolved_variables)

        #    # Expand template
        #    # term = term.expand(var_dict=resolved_variables)
        #else:
        #    raise NameError(f'Template is empty: {self._term}')
        #return str(term)

        term = URITemplate(self._term)
        variables = term.variables
        term = str(term)

        if variables:
            for var in variables:
                var = str(var)
                resolved_var = self._resolve_reference(var, data)
                var = '{' + var + '}'
                term = term.replace(var, resolved_var)
                print(term)
        else:
            raise NameError(f'Template is empty: {self._term}')

        return term

    def _resolve_reference(self, reference, data) -> str:
        # XPath reference (XML)
        if self._reference_formulation == MIMEType.APPLICATION_XML or \
           self._reference_formulation == MIMEType.TEXT_XML:
            try:
                ref = data.xpath(reference)[0]
                ref = ref.text
                return ref
            except IndexError:
                raise NameError(f'Reference {reference} invalid XPath')
        # JSONPath reference (JSON)
        elif self._reference_formulation == MIMEType.JSON:
            try:
                jsonpath = parse(reference)
                ref = jsonpath.find(data)[0]
                ref = ref.value
                return ref
            except:
                raise NameError(f'Reference {reference} invalid JSONPath')
        # Key-Value reference (CSV, TSV, SQL, RDF, SPARQL, Hydra, ...)
        elif self._reference_formulation == MIMEType.CSV or \
             self._reference_formulation == MIMEType.TSV or \
             self._reference_formulation == MIMEType.SQL or \
             self._reference_formulation == MIMEType.JSON_LD or \
             self._reference_formulation == MIMEType.N3 or \
             self._reference_formulation == MIMEType.NQUADS or \
             self._reference_formulation == MIMEType.NTRIPLES or \
             self._reference_formulation == MIMEType.RDF_XML or \
             self._reference_formulation == MIMEType.TRIG or \
             self._reference_formulation == MIMEType.TRIX or \
             self._reference_formulation == MIMEType.TURTLE:
            try:
                ref = data[reference]
                return ref
            except KeyError:
                raise NameError(f'Reference {reference} not found in {data}')
        else:
            raise ValueError('Unknown MIMEType: {self._reference_formulation}')

# Expose classes at module level
from rml.maps.subject_map import SubjectMap
from rml.maps.predicate_map import PredicateMap
