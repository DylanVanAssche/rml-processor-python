from logging import debug, critical
from lxml import etree
from lxml.etree import Element

from rml.io.sources import LogicalSource, MIMEType


class XMLLogicalSource(LogicalSource):
    def __init__(self, rml_iterator: str, path: str):
        """
        An XML Logical Source to iterate over XML data.
        The RML iterator is an XPath expression.
        """
        super().__init__(rml_iterator)
        self._path = path
        debug(f'Path: {self._path}')

        # Parse XML file
        with open(self._path) as f:
            self._iterator = etree.parse(f)

        # Apply XPath expression
        try:
            self._iterator = self._iterator.xpath(self._rml_iterator)
            self._iterator = iter(self._iterator)
        # Syntax error in XPath
        except Exception as e:
            msg = f'Reference {self._rml_iterator} invalid XPath: {e}'
            critical(msg)
            raise NameError(msg)

        debug('Source initialization complete')

    def __next__(self) -> Element:
        """
        Returns an XML element from the XML iterator.
        raises StopIteration when exhausted.
        """
        result: Element = next(self._iterator)
        debug(f'Iterator: {result}')
        return result

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.TEXT_XML
        """
        return MIMEType.TEXT_XML
