#!/usr/bin/env python

import unittest

from rml.sources import LogicalSource
print('Logical Source')

class MockLogicalSource(LogicalSource):
    def __init__(self):
        super().__init__()

    def __next__(self):
        # Abstract method mocking
        return 0

class LogicalSourceTests(unittest.TestCase):
    def test_is_iterator(self) -> None:
        mock = MockLogicalSource()
        self.assertTrue(hasattr(mock, '__iter__'))
        self.assertTrue(hasattr(mock, '__next__'))
        self.assertTrue(callable(mock.__iter__))
        self.assertTrue(mock.__iter__() is mock)

if __name__ == '__main__':
    unittest.main()
