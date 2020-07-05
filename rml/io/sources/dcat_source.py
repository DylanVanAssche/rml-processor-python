from requests import get, Response
from requests.exceptions import HTTPError, ConnectionError
from csv import DictReader, Sniffer
from os import makedirs
from os.path import basename
from lxml.etree import Element
from typing import Dict, Union

from rml.io.sources import *

TMP_DIR = '/tmp'
ITER_BYTES = 1024


class DCATLogicalSource(LogicalSource):
    def __init__(self, url: str, format: MIMEType,
                 reference_formulation: str = '', tmp_dir: str = TMP_DIR,
                 delimiter: str = ','):
        """
        A DCAT Logical Source to retrieve data from the Web and iterate over
        it.
        The RML reference formulation is not used for row-based iterators,
        but is used for XML (XPath) or JSON (JSONPath) data.
        """
        super().__init__(reference_formulation)
        self._url: str = url
        self._tmp_dir: str = tmp_dir
        self._delimiter: str = delimiter
        self._format: MIMEType = format
        self._source: LogicalSource

        # Get file from DCAT catalogue
        try:
            response: Response = get(self._url)
            response.raise_for_status()
        except (HTTPError, ConnectionError) as e:
            raise FileNotFoundError('Unable to retrieve {self._url}: {e}')

        # Store file temporary in /tmp
        makedirs(TMP_DIR, exist_ok=True)
        file_name: str = basename(self._url)
        with open(f'{self._tmp_dir}/{file_name}', 'wb') as tmp_file:
            for block in response.iter_content(ITER_BYTES):
                tmp_file.write(block)

        # Select right logical source depending on HTTP Content-Type header
        f: str = self._format.value
        if f == MIMEType.CSV.value \
                or f == MIMEType.TSV.value:
            self._source = CSVLogicalSource(f'{self._tmp_dir}/{file_name}',
                                            self._delimiter)
        elif f == MIMEType.JSON.value:
            self._source = JSONLogicalSource(self._reference_formulation,
                                             f'{self._tmp_dir}/{file_name}')
        elif f == MIMEType.TEXT_XML.value or \
                f == MIMEType.APPLICATION_XML.value:
            self._source = XMLLogicalSource(self._reference_formulation,
                                            f'{self._tmp_dir}/{file_name}')
        elif f == MIMEType.RDF_XML.value or \
                f == MIMEType.JSON_LD.value or \
                f == MIMEType.N3.value or \
                f == MIMEType.NQUADS.value or \
                f == MIMEType.NTRIPLES.value or \
                f == MIMEType.TRIG.value or \
                f == MIMEType.TRIX.value or \
                f == MIMEType.TURTLE.value:
            self._source = RDFLogicalSource(f'{self._tmp_dir}/{file_name}',
                                            self._reference_formulation,
                                            self._format)
        else:
            raise ValueError(f'Unsupported MIME type: {self._format}')

    def __next__(self) -> Union[Dict, Element]:
        """
        Returns a row from the underlying source.
        Raises StopIteration when exhausted.
        """
        return next(self._source)
