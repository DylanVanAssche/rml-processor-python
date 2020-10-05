#!/usr/bin/env python

import unittest
from typing import Dict

from rml.io.sources import LogicalSource, MIMEType


class MockLogicalSource(LogicalSource):
    def __init__(self) -> None:
        super().__init__()

    def __next__(self) -> Dict:
        # Abstract method mocking
        return {'id': 0}

    @property
    def mime_type(self) -> MIMEType:
        # Abstract method mocking
        return MIMEType.JSON


class LogicalSourceTests(unittest.TestCase):
    def test_is_iterator(self) -> None:
        mock = MockLogicalSource()
        self.assertTrue(hasattr(mock, '__iter__'))
        self.assertTrue(hasattr(mock, '__next__'))
        self.assertTrue(callable(mock.__iter__))
        self.assertTrue(mock.__iter__() is mock)

    def test_mime_type(self) -> None:
        """
        Test the MIME type property
        """
        mock = MockLogicalSource()
        self.assertEqual(mock.mime_type, MIMEType.JSON)


if __name__ == '__main__':
    unittest.main()
