from requests import get, Response
from requests.exceptions import HTTPError, ConnectionError
from csv import DictReader, Sniffer
from os.path import basename
from os import remove
from rdflib import URIRef
from typing import Dict
from tempfile import NamedTemporaryFile

from rml.io.sources import *
from rml.namespace import HYDRA

ITER_BYTES = 1024


class HydraLogicalSource(LogicalSource):
    def __init__(self, url: str, format: MIMEType,
                 reference_formulation: str = '') -> None:
        """
        A Hydra Logical Source to retrieve data from a Hydra Web API and
        iterate over it.
        The RML reference formulation is not used for row-based iterators,
        but is used for XML (XPath) or JSON (JSONPath) data.
        """
        super().__init__(reference_formulation)
        self._url: str = url
        self._format: MIMEType = format
        self._next_page: URIRef
        self._tmp_file: str

        # Verify format
        f: str = self._format.value
        if f == MIMEType.RDF_XML.value or \
                f == MIMEType.JSON_LD.value or \
                f == MIMEType.N3.value or \
                f == MIMEType.NQUADS.value or \
                f == MIMEType.NTRIPLES.value or \
                f == MIMEType.TRIG.value or \
                f == MIMEType.TRIX.value or \
                f == MIMEType.TURTLE.value:
            # Start fetching if format is supported
            self._fetch(self._url)
        else:
            raise ValueError(f'Unsupported MIME type: {self._format}')

    def _fetch(self, url: str) -> None:
        """
        Fetch a Hydra fragment.
        Raises StopIteration if no next fragment exists.
        """

        # Get Hydra fragment
        try:
            response: Response = get(url)
            response.raise_for_status()
        except (HTTPError, ConnectionError) as e:
            raise FileNotFoundError('Unable to retrieve {url}: {e}')

        # Store Hydra response temporary in /tmp
        with NamedTemporaryFile(delete=False) as tmp_file:
            self._tmp_file = tmp_file.name
            for block in response.iter_content(ITER_BYTES):
                tmp_file.write(block)

        # Update source
        path: str = self._tmp_file
        rf: str = self._reference_formulation
        format: MIMEType = self._format
        self._source: RDFLogicalSource = RDFLogicalSource(path, rf, format)

        # Try to get the next page
        try:
            subj: URIRef
            obj: URIRef
            subj, obj = next(self._source.graph.subject_objects(HYDRA.next))
            self._next_page = obj
        except StopIteration:
            # Raising StopIteration would stop the iteration immediately and
            # misses the current page (last page)
            self._next_page = None

    def __next__(self) -> Dict:
        """
        Returns a row from the underlying source.
        Raises StopIteration when exhausted.
        """
        try:
            return next(self._source)
        except StopIteration:
            if self._next_page is not None:
                # Current Hydra fragment exhausted, try to fetch the next one
                print(f'Fetching next page: {self._next_page}')
                self._fetch(self._next_page)
                return next(self._source)
            else:
                if self._tmp_file is not None:
                    remove(self._tmp_file)
                raise StopIteration
