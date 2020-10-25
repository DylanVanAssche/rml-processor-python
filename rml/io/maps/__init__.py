import re
from urllib.parse import quote
from abc import ABC, abstractmethod
from enum import Enum, unique
from rdflib.term import Identifier
from jsonpath_ng import parse, JSONPath
from jsonpath_ng.parser import JsonPathParser
from lxml import etree
from lxml.etree import Element
from typing import List, Union, Dict, Optional, cast

from rml.namespace import R2RML, RML
from rml.namespace.xmls import SPARQL_RESULTS_PREFIX, SPARQL_RESULTS_NS
from rml.io.sources import MIMEType

JSONPATH_SPLIT_PATTERN = re.compile(r'\$|\.|\[|\]|\(|\)|\@|\*')
URITEMPLATE_PATTERN = re.compile(r'\{(.*?)\}')
NS = {SPARQL_RESULTS_PREFIX: SPARQL_RESULTS_NS}


@unique
class TermType(Enum):
    CONSTANT = R2RML.constant
    TEMPLATE = R2RML.template
    REFERENCE = RML.reference
    UNKNOWN = 'UNKNOWN'  # Used for unittests


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
        """
        Resolves a string template.
        """
        term: str = self._term
        variables: List[str] = URITEMPLATE_PATTERN.findall(self._term)

        if variables:
            for v in variables:
                var: str = str(v)
                resolved_var: str = self._resolve_reference(var, data)
                var = '{' + var + '}'

                # Precent encoding of each term if rr:termType is rr:IRI
                if self._term.startswith('http://') or \
                        self._term.startswith('https://'):
                    resolved_var = quote(resolved_var)

                term = term.replace(var, resolved_var)
        else:
            raise NameError(f'Template is empty: {self._term}')

        return term

    def _resolve_reference(self, reference: str,
                           data: Union[Element, Dict]) -> str:
        """
        Resolves a reference.
        """
        # XPath reference (XML)
        if self._reference_formulation == MIMEType.APPLICATION_XML or \
           self._reference_formulation == MIMEType.TEXT_XML:
            xml: str
            try:
                xml_ref: Element = cast(Element, data).xpath(reference,
                                                             namespaces=NS)[0]
                value = str(xml_ref.text)
                # No result: empty string
                if not value.strip():
                    xml = etree.tostring(cast(Element, data),
                                         pretty_print=True)
                    raise ResourceWarning(f'Reference {reference} not found in'
                                          f'{xml}')
                return value
            # Avoid catching ResourceWarning as Exception below
            except ResourceWarning as w:
                raise w
            # No result: reference 0 results
            except IndexError:
                xml = etree.tostring(cast(Element, data), pretty_print=True)
                raise ResourceWarning(f'Reference {reference} not found in '
                                      f'{xml}')
            # Syntax error in XPath
            except Exception as e:
                raise NameError(f'Reference {reference} invalid XPath: {e}')
        # JSONPath reference (JSON)
        elif self._reference_formulation == MIMEType.JSON:
            try:
                # JSONPath module cannot deal with spaces without escaping them
                reference = self._escape_spaces_jsonpath(reference)
                jsonpath: JsonPathParser = parse(reference)
                json_ref: JSONPath = jsonpath.find(cast(Dict, data))
                json_ref = json_ref[0]
                # No result: value is None
                if json_ref.value is None:
                    raise ResourceWarning(f'Reference {reference} not found in'
                                          f' {data}')
                return str(json_ref.value)
            # Avoid catching ResourceWarning as Exception below
            except ResourceWarning as w:
                raise w
            # No result: reference 0 results
            except IndexError:
                raise ResourceWarning(f'Reference {reference} not found in '
                                      f'{data}')
            # Syntax error in JSONPath
            except Exception as e:
                raise NameError(f'Reference {reference} invalid JSONPath: {e}')

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
                # Strip quoting SQL dialects
                reference = reference.strip('\"')  # PostgreSQL
                reference = reference.strip('`')  # MySQL
                reference = reference.strip('[').strip(']')  # MSSQL
                value = cast(Dict, data)[reference]
                if value is None:
                    raise ResourceWarning(f'Reference {reference} value is '
                                          f'None in {data}')
                return str(value)
            # No result: column not in row
            except KeyError as e:
                # Tabular data: fixed columns. Column not available, raise
                # error to stop the execution
                if self._reference_formulation == MIMEType.CSV or \
                        self._reference_formulation == MIMEType.TSV or \
                        self._reference_formulation == MIMEType.SQL:
                    raise NameError(f'Reference {reference} not found in '
                                    f'{data}')
                # Other data: unfixed data schema. Reference not available,
                # raise warning to ignore the triple
                else:
                    raise ResourceWarning(f'Reference {reference} not found in'
                                          f' {data}')
        else:
            raise ValueError('Unknown MIMEType: {self._reference_formulation}')

    def _escape_spaces_jsonpath(self, path: str) -> str:
        if ' ' in path:
            for field in JSONPATH_SPLIT_PATTERN.split(path):
                path = path.replace(field, ''.join(['\'', field, '\'']))
        return path


# Expose classes at module level
from rml.io.maps.subject_map import SubjectMap  # nopep8
from rml.io.maps.predicate_map import PredicateMap  # nopep8
from rml.io.maps.object_map import ObjectMap  # nopep8
from rml.io.maps.predicate_object_map import PredicateObjectMap  # nopep8
from rml.io.maps.triples_map import TriplesMap  # nopep8
