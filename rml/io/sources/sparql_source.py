import re
from logging import debug, critical
from enum import Enum
from abc import ABC, abstractmethod
from io import StringIO
from SPARQLWrapper import SPARQLWrapper, JSON, XML
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound
from jsonpath_ng import parse
from lxml import etree
from lxml.etree import XPathEvalError, Element
from requests import get, HTTPError
from typing import Union, Dict, List
from xml.dom.minidom import Document

from rml.io.sources import LogicalSource, MIMEType
from rml.namespace.xmls import SPARQL_RESULTS_PREFIX, SPARQL_RESULTS_NS

NS = {SPARQL_RESULTS_PREFIX: SPARQL_RESULTS_NS}
SPARQL_SELECT_PATTERN = re.compile(r'SELECT.+WHERE')
SPARQL_VARIABLE_PATTERN = re.compile(r'(\?\w+)')


class SPARQLLogicalSource(LogicalSource, ABC):
    def __init__(self, rml_iterator: str, endpoint: str, query: str):
        """
        An SPARQL Logical Source to iterate over RDF data.
        The RML iterator is used to select the JSON results or XML
        results depending on return_format.
        """
        super().__init__(rml_iterator)
        self._query = query
        self._endpoint = endpoint
        self._return_format: str
        debug(f'Query: {self._query}')
        debug(f'SPARQL endpoint: {self._endpoint}')

        # Check duplicate variables
        q: str = re.sub('\n|\r', '', self._query)  # Strip new lines for regex
        try:
            select: str = SPARQL_SELECT_PATTERN.findall(q)[0]  # Find SELECT
            variables = SPARQL_VARIABLE_PATTERN.findall(select)  # Get vars
            if sorted(variables) != sorted(list(set(variables))):
                msg = 'SPARQL SELECT query must contain unique variable '
                f'names: {variables}'
                critical(msg)
                raise ValueError(msg)
        except IndexError:
            msg = 'SPARQL query must be a SPARQL SELECT query: '
            f'{self._query}'
            critical(msg)
            raise ValueError(msg)

        debug('Source initialization complete')

    def _execute_query(self) -> None:
        self._engine = SPARQLWrapper(self._endpoint,
                                     returnFormat=self._return_format)
        self._engine.setQuery(self._query)

    @abstractmethod
    def _parse_results(self) -> None:
        """
        Parse SPARQL results, parsing depends on self._return_format
        """

    @abstractmethod
    def __next__(self) -> Union[Dict, Element]:
        """
        Iterates over SPARQL results, iteration depends on self._return_format
        """

    @property
    @abstractmethod
    def mime_type(self) -> MIMEType:
        """
        The MIME type of the SPARQL results.
        """


class SPARQLJSONLogicalSource(SPARQLLogicalSource):
    def __init__(self, rml_iterator: str, endpoint: str, query: str):
        """
        An SPARQL JSON Logical Source to iterate over RDF data with results
        returned as JSON.
        """
        super().__init__(rml_iterator, endpoint, query)
        self._return_format = JSON
        self._execute_query()
        self._parse_results()
        debug(f'SPARQL results format: {self._return_format}')

    def _parse_results(self) -> None:
        """
        Parse SPARQL results as JSON using a JSONPath expression
        """
        # Parse JSONPath expression
        try:
            self._iterator = parse(self._rml_iterator)
        except Exception as e:
            msg = f'Invalid JSONPath: {self._rml_iterator}: {e}'
            critical(msg)
            raise ValueError(msg)

        # Parse SPARQL JSON results
        try:
            results: Dict = self._engine.queryAndConvert()
        except EndPointNotFound as e:
            msg = f'Endpoint {self._endpoint} not found: {e}'
            critical(msg)
            raise FileNotFoundError(msg)

        # Find JSONPath results
        self._iterator = iter(self._iterator.find(results))

    def __next__(self) -> Dict:
        """
        Returns a result from the SPARQL iterator.
        raises StopIteration when exhausted.
        """
        result: Dict = next(self._iterator).value
        debug('Result: {result}')
        return result

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.JSON.
        """
        return MIMEType.JSON


class SPARQLXMLLogicalSource(SPARQLLogicalSource):
    def __init__(self, rml_iterator: str, endpoint: str, query: str):
        """
        An SPARQL XML Logical Source to iterate over RDF data with results
        returned as XML.
        """
        super().__init__(rml_iterator, endpoint, query)
        self._return_format = XML
        self._execute_query()
        self._parse_results()
        debug(f'SPARQL results format: {self._return_format}')

    def _parse_results(self) -> None:
        """
        Parse SPARQL results as XML using an XPath expression
        """
        # Parse SPARQL XML results
        try:
            results: Document = self._engine.queryAndConvert()
            tree: Element = etree.fromstring(str(results.toxml()))
        except EndPointNotFound as e:
            msg = f'Endpoint {self._endpoint} not found: {e}'
            critical(msg)
            raise FileNotFoundError(msg)

        # Apply XPath expression
        try:
            self._iterator = tree.xpath(self._rml_iterator,
                                        namespaces=NS)
            self._iterator = iter(self._iterator)
        except XPathEvalError as e:
            msg = f'Invalid XPath: {self._rml_iterator}: {e}'
            critical(msg)
            raise ValueError(msg)

    def __next__(self) -> Element:
        """
        Returns an XML element from the XML iterator.
        raises StopIteration when exhausted.
        """
        result: Element = next(self._iterator)
        debug('Result: {etree.tostring(result, pretty_print=True)}')
        return result

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.TEXT_XML.
        """
        return MIMEType.TEXT_XML
