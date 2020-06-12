from enum import Enum
from abc import ABC, abstractmethod
from io import StringIO
from SPARQLWrapper import SPARQLWrapper, JSON, XML
from jsonpath_ng import parse
from lxml import etree
from lxml.etree import XPathEvalError
from requests import get, HTTPError

from . import LogicalSource

class SPARQLLogicalSource(LogicalSource, ABC):
    def __init__(self, reference_formulation: str, endpoint: str, query: str):
        """
        An SPARQL Logical Source to iterate over RDF data.
        The RML reference formulation is used to select the JSON results or XML
        results depending on return_format.
        """
        super().__init__(reference_formulation)
        self._query = query
        self._endpoint = endpoint

    def _check_endpoint(self):
        try:
            get(self._endpoint).raise_for_status()
        except HTTPError:
            raise FileNotFoundError

    def _execute_query(self):
        self._engine = SPARQLWrapper(self._endpoint,
                                     returnFormat=self._return_format)
        self._engine.setQuery(self._query)

    @abstractmethod
    def _parse_results(self):
        """
        Parse SPARQL results, parsing depends on self._return_format
        """

    @abstractmethod
    def __next__(self):
        """
        Iterates over SPARQL results, iteration depends on self._return_format
        """

class SPARQLJSONLogicalSource(SPARQLLogicalSource):
    def __init__(self, reference_formulation: str, endpoint: str, query: str):
        """
        An SPARQL JSON Logical Source to iterate over RDF data with results
        returned as JSON.
        """
        super().__init__(reference_formulation, endpoint, query)
        self._return_format = JSON
        self._check_endpoint()
        self._execute_query()
        self._parse_results()

    def _parse_results(self):
        """
        Parse SPARQL results as JSON using a JSONPath expression
        """
        try:
            self._iterator = parse(self._reference_formulation)
        except:
            raise ValueError('Invalid JSONPath expression')

        results = self._engine.query().convert()
        self._iterator = iter(self._iterator.find(results))

    def __next__(self):
        """
        Returns a result from the SPARQL iterator.
        raises StopIteration when exhausted.
        """
        return next(self._iterator).value

class SPARQLXMLLogicalSource(SPARQLLogicalSource):
    def __init__(self, reference_formulation: str, endpoint: str, query: str):
        """
        An SPARQL XML Logical Source to iterate over RDF data with results
        returned as XML.
        """
        super().__init__(reference_formulation, endpoint, query)
        self._return_format = XML
        self._check_endpoint()
        self._execute_query()
        self._parse_results()

    def _parse_results(self):
        """
        Parse SPARQL results as XML using an XPath expression
        """
        # Parse XML file
        results = self._engine.query().convert()
        results = StringIO(results.toxml())
        self._iterator = etree.parse(results, etree.HTMLParser())

        # Apply XPath expression
        try:
            self._iterator = self._iterator.xpath(self._reference_formulation)
        except XPathEvalError:
            raise ValueError(f'Invalid XPath expression: {self._reference_formulation}')

    def __next__(self):
        """
        Returns an XML element from the XML iterator.
        raises StopIteration when exhausted.
        """
        try:
            children = {}
            element = self._iterator.pop(0)
            # If children, return children's text of element
            if len(element):
                for child in element:
                    children[child.tag] = child.text
                return children
            # No children, return element's text
            else:
                return element.text
        except IndexError:
            raise StopIteration
