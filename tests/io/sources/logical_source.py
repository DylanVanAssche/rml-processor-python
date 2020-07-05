#!/usr/bin/env python

import unittest
from typing import Dict

from rml.io.sources import LogicalSource


class MockLogicalSource(LogicalSource):
    def __init__(self) -> None:
        super().__init__()

    def __next__(self) -> Dict:
        # Abstract method mocking
        return {'id': 0}


class LogicalSourceTests(unittest.TestCase):
    def test_is_iterator(self) -> None:
        mock = MockLogicalSource()
        self.assertTrue(hasattr(mock, '__iter__'))
        self.assertTrue(hasattr(mock, '__next__'))
        self.assertTrue(callable(mock.__iter__))
        self.assertTrue(mock.__iter__() is mock)


if __name__ == '__main__':
    unittest.main()
