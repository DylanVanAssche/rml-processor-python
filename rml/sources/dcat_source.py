from requests import get
from requests.exceptions import HTTPError, ConnectionError
from csv import DictReader, Sniffer
from enum import Enum
from os import makedirs
from os.path import basename

from . import LogicalSource, CSVLogicalSource, JSONLogicalSource, XMLLogicalSource

TMP_DIR='/tmp'
ITER_BYTES=1024

class MIMEType(Enum):
    CSV = 'text/csv'
    TSV = 'text/tab-separated-values'
    JSON = 'application/json'
    XML = 'application/xml'

class DCATLogicalSource(LogicalSource):
    def __init__(self, url : str, reference_formulation: str='', tmp_dir=TMP_DIR,
                 delimiter=','):
        """
        A DCAT Logical Source to retrieve data from the Web and iterate over
        it.
        The RML reference formulation is not used for row-based iterators,
        but is used for XML (XPath) or JSON (JSONPath) data.
        Data type is detected by the Content-Type HTTP header.
        """
        super().__init__(reference_formulation)
        self._url = url
        self._tmp_dir = tmp_dir
        self._delimiter = delimiter

        # Get file from DCAT catalogue
        try:
            response = get(self._url)
            response.raise_for_status()
        except (HTTPError, ConnectionError) as e:
            raise FileNotFoundError('Unable to retrieve {self._url}: {e}')

        # Store file temporary in /tmp
        makedirs(TMP_DIR, exist_ok=True)
        file_name = basename(self._url)
        with open(f'{self._tmp_dir}/{file_name}', 'wb') as f:
            for block in response.iter_content(ITER_BYTES):
                f.write(block)

        # Select right logical source depending on HTTP Content-Type header
        content_type = response.headers['content-type']
        if content_type == MIMEType.CSV.value \
           or content_type == MIMEType.TSV.value:
            self._source = CSVLogicalSource(f'{self._tmp_dir}/{file_name}',
                                            self._delimiter)
        elif content_type == MIMEType.JSON.value:
            self._source = JSONLogicalSource(self._reference_formulation,
                                             f'{self._tmp_dir}/{file_name}')
        elif content_type == MIMEType.XML.value:
            self._source = XMLLogicalSource(self._reference_formulation,
                                            f'{self._tmp_dir}/{file_name}')
        else:
            raise ValueError(f'Unsupported HTTP Content-Type: {content_type}')

    def __next__(self):
        """
        Returns a row from the underlying source.
        Raises StopIteration when exhausted.
        """
        return next(self._source)
