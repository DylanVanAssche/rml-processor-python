from lxml import etree

from . import LogicalSource

class XMLLogicalSource(LogicalSource):
    def __init__(self, reference_formulation: str, path: str):
        """
        An XML Logical Source to iterate over XML data.
        The RML reference formulation is an XPath expression.
        """
        super().__init__(reference_formulation)
        self._path = path
        self._file = open(self._path)

        # Parse XML file
        self._iterator = etree.parse(self._file)

        # Apply XPath expression
        self._iterator = self._iterator.xpath(self._reference_formulation)

    def __next__(self):
        """
        Returns an XML element from the XML iterator.
        raises StopIteration when exhausted.
        """
        try:
            children = {}
            element = self._iterator.pop(0)
            for child in element:
                children[child.tag] = child.text
            return children
        except IndexError:
            self._file.close()
            raise StopIteration
