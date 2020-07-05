from requests import get, Response
from requests.exceptions import HTTPError, ConnectionError
from csv import DictReader, Sniffer
from os import makedirs
from os.path import basename
from rdflib import URIRef
from typing import Dict

from rml.io.sources import *

TMP_DIR='/tmp'
ITER_BYTES=1024

class Hydra(Enum):
    NEXT = URIRef('http://www.w3.org/ns/hydra/core#next')
    PREVIOUS = URIRef('http://www.w3.org/ns/hydra/core#previous')

class HydraLogicalSource(LogicalSource):
    def __init__(self, url : str, format: MIMEType,
            reference_formulation: str='', tmp_dir: str = TMP_DIR) -> None:
        """
        A Hydra Logical Source to retrieve data from a Hydra Web API and
        iterate over it.
        The RML reference formulation is not used for row-based iterators,
        but is used for XML (XPath) or JSON (JSONPath) data.
        """
        super().__init__(reference_formulation)
        self._url: str = url
        self._tmp_dir: str = tmp_dir
        self._format: MIMEType = format
        self._next_page: URIRef

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
        makedirs(TMP_DIR, exist_ok=True)
        file_name: str = basename(url)
        with open(f'{self._tmp_dir}/{file_name}', 'wb') as tmp_file:
            for block in response.iter_content(ITER_BYTES):
                tmp_file.write(block)

        # Update source
        self._source: RDFLogicalSource = RDFLogicalSource(f'{self._tmp_dir}/{file_name}',
                                        self._reference_formulation,
                                        self._format)
        # Try to get the next page
        try:
            subj: URIRef
            obj: URIRef
            subj, obj = next(self._source.graph.subject_objects(Hydra.NEXT.value))
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
                raise StopIteration
