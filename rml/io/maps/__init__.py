import re
from logging import debug, warning, critical
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
        self._mime_type: MIMEType = reference_formulation
        debug(f'Term: {self._term}')
        debug(f'Term type: {self._term_type}')
        debug(f'MIME type: {self._mime_type}')  # Gitlab bug
        debug(f'Term Map initialization complete')

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
            debug(f'Variables: {variables} from {self._term}')
            for v in variables:
                var: str = str(v)
                resolved_var: str = self._resolve_reference(var, data)
                var = '{' + var + '}'

                # Precent encoding of each term if rr:termType is rr:IRI
                if self._term.startswith('http://') or \
                        self._term.startswith('https://'):
                    resolved_var = quote(resolved_var)

                term = term.replace(var, resolved_var)
                debug(f'Replaced {var} with {resolved_var}')
        else:
            msg = f'Template is empty: {self._term}'
            critical(msg)
            raise NameError(msg)

        debug(f'Resolved template: {term}')
        return term

    def _resolve_reference(self, reference: str,
                           data: Union[Element, Dict]) -> str:
        """
        Resolves a reference.
        """
        # XPath reference (XML)
        if self._mime_type == MIMEType.APPLICATION_XML or \
           self._mime_type == MIMEType.TEXT_XML:
            xml: str
            try:
                xml_ref: Element = cast(Element, data).xpath(reference,
                                                             namespaces=NS)[0]
                value_xml: str = str(xml_ref.text)
                # No result: empty string
                if not value_xml.strip():
                    xml = etree.tostring(cast(Element, data),
                                         pretty_print=True)
                    msg = f'Reference {reference} not found in {xml}'
                    warning(msg)
                    raise ResourceWarning(msg)
                return value_xml
            # Avoid catching ResourceWarning as Exception below
            except ResourceWarning as w:
                raise w
            # No result: reference 0 results
            except IndexError:
                xml = etree.tostring(cast(Element, data), pretty_print=True)
                msg = f'Reference {reference} not found in {xml}'
                warning(msg)
                raise ResourceWarning(msg)
            # Syntax error in XPath
            except Exception as e:
                msg = f'Reference {reference} invalid XPath: {e}'
                raise NameError(msg)
        # JSONPath reference (JSON)
        elif self._mime_type == MIMEType.JSON:
            try:
                # JSONPath module cannot deal with spaces without escaping them
                reference = self._escape_spaces_jsonpath(reference)
                jsonpath: JsonPathParser = parse(reference)
                json_ref: JSONPath = jsonpath.find(cast(Dict, data))
                json_ref = json_ref[0]
                value_json = json_ref.value
                # No result: value is None
                if value_json is None:
                    msg = f'Reference {reference} is None in {data}'
                    warning(msg)
                    raise ResourceWarning(msg)
                return str(value_json)
            # Avoid catching ResourceWarning as Exception below
            except ResourceWarning as w:
                raise w
            # No result: reference 0 results
            except IndexError:
                msg = f'Reference {reference} not found in {data}'
                warning(msg)
                raise ResourceWarning(msg)
            # Syntax error in JSONPath
            except Exception as e:
                msg = f'Reference {reference} invalid JSONPath: {e}'
                critical(msg)
                raise NameError(msg)

        # Key-Value reference (CSV, TSV, SQL, RDF, SPARQL, Hydra, ...)
        elif self._mime_type == MIMEType.CSV or \
                self._mime_type == MIMEType.TSV or \
                self._mime_type == MIMEType.SQL or \
                self._mime_type == MIMEType.JSON_LD or \
                self._mime_type == MIMEType.N3 or \
                self._mime_type == MIMEType.NQUADS or \
                self._mime_type == MIMEType.NTRIPLES or \
                self._mime_type == MIMEType.RDF_XML or \
                self._mime_type == MIMEType.TRIG or \
                self._mime_type == MIMEType.TRIX or \
                self._mime_type == MIMEType.TURTLE:
            try:
                # Strip quoting SQL dialects
                reference = reference.strip('\"')  # PostgreSQL
                reference = reference.strip('`')  # MySQL
                reference = reference.strip('[').strip(']')  # MSSQL
                value_kv = cast(Dict, data)[reference]
                # No result: value is None
                if value_kv is None:
                    msg = f'Reference {reference} is None in {data}'
                    warning(msg)
                    raise ResourceWarning(msg)
                return str(value_kv)
            # No result: column not in row
            except KeyError as e:
                # Tabular data: fixed columns. Column not available, raise
                # error to stop the execution
                if self._mime_type == MIMEType.CSV or \
                        self._mime_type == MIMEType.TSV or \
                        self._mime_type == MIMEType.SQL:
                    msg = f'Reference {reference} not found in {data}'
                    critical(msg)
                    raise NameError(msg)
                # Other data: unfixed data schema. Reference not available,
                # raise warning to ignore the triple
                else:
                    msg = f'Reference {reference} not found in {data}'
                    warning(msg)
                    raise ResourceWarning(msg)
        else:
            msg = f'Unknown MIMEType: {self._mime_type}'
            critical(msg)
            raise ValueError(msg)

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
