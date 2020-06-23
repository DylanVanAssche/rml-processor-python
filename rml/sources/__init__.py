#!/usr/bin/env python

from abc import ABC, abstractmethod
from enum import Enum

class LogicalSource(ABC):
    def __init__(self, reference_formulation: str = '') -> None:
        self._reference_formulation = reference_formulation

    def __iter__(self) -> iter:
        """
        Every LogicalSource instance is a Python iterator
        """
        return self

    @abstractmethod
    def __next__(self) -> dict:
        """
        __next__() method must be implemented by every subclass.
        This methods provides the next value of the iterator
        """

class MIMEType(Enum):
    SQL = 'sql'
    CSV = 'text/csv'
    TSV = 'text/tab-separated-values'
    JSON = 'application/json'
    APPLICATION_XML = 'application/xml'
    TEXT_XML = 'text/xml'
    RDF_XML = 'application/rdf+xml'
    JSON_LD = 'application/ld+json'
    TRIX = 'trix' # MIME type = text/xml
    TRIG = 'trig' # MIME type = text/turtle
    N3 = 'text/n3'
    NQUADS = 'application/n-quads'
    TURTLE = 'turtle' # MIME type = text/turtle
    NTRIPLES = 'nt' # MIME type = text/plain
    UNKNOWN = 'unknown' # Unsupported MIME type

# Expose classes at module level
from rml.sources.csv_source import CSVLogicalSource
from rml.sources.json_source import JSONLogicalSource
from rml.sources.xml_source import XMLLogicalSource
from rml.sources.sql_source import SQLLogicalSource
from rml.sources.sparql_source import SPARQLJSONLogicalSource, SPARQLXMLLogicalSource
from rml.sources.rdf_source import RDFLogicalSource
from rml.sources.dcat_source import DCATLogicalSource
from rml.sources.hydra_source import HydraLogicalSource
