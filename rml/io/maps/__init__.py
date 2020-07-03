from abc import ABC, abstractmethod
from enum import Enum
from rdflib.term import Identifier
from uritemplate import URITemplate
from uritemplate.variable import URIVariable
from jsonpath_ng import parse, JSONPath
from jsonpath_ng.parser import JsonPathParser
from lxml.etree import Element
from typing import List, Union, Dict, cast

from rml.namespace import R2RML, RML
from rml.io.sources import MIMEType

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
        self._term: str = term
        self._term_type: TermType = term_type
        self._reference_formulation: MIMEType = reference_formulation

    @abstractmethod
    def resolve(self, data: Union[Element, Dict]) -> Identifier:
        """
        Resolve the given term as RDF IRI or RDF Literal.
        """

    def _resolve_template(self, data: Union[Element, Dict]) -> str:
        #######################################################################
        # uritemplate has a builtin method to replace variables
        # (term.expand()), but it follows the RFC specification too strict,
        # XPatp expression with '/' are not allowed according to the RFC
        # specification.
        # https://github.com/python-hyper/uritemplate/issues/56
        #######################################################################
        template: URITemplate = URITemplate(self._term)
        variables: List[URIVariable] = template.variables
        term: str = str(template)

        if variables:
            for v in variables:
                var: str = str(v)
                resolved_var: str = self._resolve_reference(var, data)
                var = '{' + var + '}'
                term = term.replace(var, resolved_var)
        else:
            raise NameError(f'Template is empty: {self._term}')

        return term

    def _resolve_reference(self, reference: str, data: Union[Element, Dict]) -> str:
        # XPath reference (XML)
        if self._reference_formulation == MIMEType.APPLICATION_XML or \
           self._reference_formulation == MIMEType.TEXT_XML:
            try:
                xml_ref: Element = cast(Element, data) .xpath(reference)[0]
                return str(xml_ref.text)
            except IndexError:
                raise NameError(f'Reference {reference} invalid XPath')
        # JSONPath reference (JSON)
        elif self._reference_formulation == MIMEType.JSON:
            try:
                jsonpath: JsonPathParser = parse(reference)
                json_ref: JSONPath = jsonpath.find(cast(Dict, data))[0]
                return str(json_ref.value)
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
                return str(cast(Dict, data)[reference])
            except KeyError:
                raise NameError(f'Reference {reference} not found in {data}')
        else:
            raise ValueError('Unknown MIMEType: {self._reference_formulation}')

# Expose classes at module level
from rml.io.maps.subject_map import SubjectMap
from rml.io.maps.predicate_map import PredicateMap
from rml.io.maps.object_map import ObjectMap
from rml.io.maps.predicate_object_map import PredicateObjectMap

from rml.io.maps.triples_map import TriplesMap
