from requests import Session, Response
from requests.exceptions import HTTPError, ConnectionError
from requests_file import FileAdapter
from csv import DictReader, Sniffer
from os import remove
from os.path import basename
from lxml.etree import Element
from typing import Dict, Union
from tempfile import NamedTemporaryFile

from rml.io.sources import LogicalSource, MIMEType, JSONLogicalSource, \
                           XMLLogicalSource, CSVLogicalSource, RDFLogicalSource

ITER_BYTES = 1024


class DCATLogicalSource(LogicalSource):
    def __init__(self, url: str, mime_type: MIMEType,
                 reference_formulation: str = '',
                 delimiter: str = ',') -> None:
        """
        A DCAT Logical Source to retrieve data from the Web and iterate over
        it.
        The RML reference formulation is not used for row-based iterators,
        but is used for XML (XPath) or JSON (JSONPath) data.
        """
        super().__init__(reference_formulation)
        self._url: str = url
        self._delimiter: str = delimiter
        self._mime_type: MIMEType = mime_type
        self._source: LogicalSource
        self._tmp_file: str
        self._session = Session()
        self._session.mount('file://', FileAdapter())  # Support local files

        # Get file from DCAT catalogue
        try:
            response: Response = self._session.get(self._url)
            response.raise_for_status()
        except (HTTPError, ConnectionError) as e:
            raise FileNotFoundError('Unable to retrieve {self._url}: {e}')

        # Store file temporary in /tmp
        with NamedTemporaryFile(delete=False) as tmp_file:
            self._tmp_file = tmp_file.name
            for block in response.iter_content(ITER_BYTES):
                tmp_file.write(block)

        # Select right logical source depending on HTTP Content-Type header
        f: str = self._mime_type.value
        if f == MIMEType.CSV.value \
                or f == MIMEType.TSV.value:
            self._source = CSVLogicalSource(self._tmp_file,
                                            self._delimiter)
        elif f == MIMEType.JSON.value:
            self._source = JSONLogicalSource(self._reference_formulation,
                                             self._tmp_file)
        elif f == MIMEType.TEXT_XML.value or \
                f == MIMEType.APPLICATION_XML.value:
            self._source = XMLLogicalSource(self._reference_formulation,
                                            self._tmp_file)
        elif f == MIMEType.RDF_XML.value or \
                f == MIMEType.JSON_LD.value or \
                f == MIMEType.N3.value or \
                f == MIMEType.NQUADS.value or \
                f == MIMEType.NTRIPLES.value or \
                f == MIMEType.TRIG.value or \
                f == MIMEType.TRIX.value or \
                f == MIMEType.TURTLE.value:
            self._source = RDFLogicalSource(self._tmp_file,
                                            self._reference_formulation,
                                            self._mime_type)
        else:
            raise ValueError(f'Unsupported MIME type: {self._mime_type}')

    def __next__(self) -> Union[Dict, Element]:
        """
        Returns a row from the underlying source.
        Raises StopIteration when exhausted.
        """
        try:
            return next(self._source)
        except StopIteration:
            if self._tmp_file is not None:
                remove(self._tmp_file)
            raise StopIteration

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns the provided MIME type of the DCAT dataset.
        """
        return self._mime_type
