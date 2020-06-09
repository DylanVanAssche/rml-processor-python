#!/usr/bin/env python

from abc import ABC, abstractmethod

class LogicalSource(ABC):
    def __init__(self, reference_formulation: str = '') -> None:
        self._reference_formulation = reference_formulation

    def __iter__(self) -> iter:
        """
        Every LogicalSource instance is a Python generator
        """
        return self

    @abstractmethod
    def __next__(self) -> dict:
        """
        __next__() method must be implemented by every subclass.
        This methods provides the next value of the generator
        """

# Expose classes at module level
from rml.sources.csv_source import CSVLogicalSource
