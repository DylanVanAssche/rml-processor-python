#!/usr/bin/env python

from typing import Iterator, Dict
from abc import ABC, abstractmethod
from enum import Enum


class LogicalSource(ABC):
    def __init__(self, reference_formulation: str = '') -> None:
        self._reference_formulation: str = reference_formulation

    def __iter__(self) -> Iterator:
        """
        Every LogicalSource instance is a Python iterator
        """
        return self

    @abstractmethod
    def __next__(self) -> Dict:
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
    TRIX = 'trix'  # MIME type = text/xml
    TRIG = 'trig'  # MIME type = text/turtle
    N3 = 'text/n3'
    NQUADS = 'application/n-quads'
    TURTLE = 'turtle'  # MIME type = text/turtle
    NTRIPLES = 'nt'  # MIME type = text/plain
    UNKNOWN = 'unknown'  # Unsupported MIME type


# Expose classes at module level
from rml.io.sources.rdf_source import RDFLogicalSource  # nopep8
from rml.io.sources.json_source import JSONLogicalSource  # nopep8
from rml.io.sources.csv_source import CSVLogicalSource  # nopep8
from rml.io.sources.sql_source import SQLLogicalSource  # nopep8
from rml.io.sources.xml_source import XMLLogicalSource  # nopep8
from rml.io.sources.sparql_source import SPARQLJSONLogicalSource, \
                                         SPARQLXMLLogicalSource  # nopep8
from rml.io.sources.hydra_source import HydraLogicalSource  # nopep8
from rml.io.sources.dcat_source import DCATLogicalSource  # nopep8
