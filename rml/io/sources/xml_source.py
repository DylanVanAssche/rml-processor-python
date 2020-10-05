from lxml import etree
from lxml.etree import Element

from rml.io.sources import LogicalSource, MIMEType


class XMLLogicalSource(LogicalSource):
    def __init__(self, reference_formulation: str, path: str):
        """
        An XML Logical Source to iterate over XML data.
        The RML reference formulation is an XPath expression.
        """
        super().__init__(reference_formulation)
        self._path = path

        # Parse XML file
        with open(self._path) as f:
            self._iterator = etree.parse(f)

        # Apply XPath expression
        self._iterator = self._iterator.xpath(self._reference_formulation)
        self._iterator = iter(self._iterator)

    def __next__(self) -> Element:
        """
        Returns an XML element from the XML iterator.
        raises StopIteration when exhausted.
        """
        return next(self._iterator)

    @property
    def mime_type(self) -> MIMEType:
        """
        Returns MIMEType.TEXT_XML
        """
        return MIMEType.TEXT_XML
