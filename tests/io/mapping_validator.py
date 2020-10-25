import unittest
from parameterized import parameterized
from glob import glob
from os.path import dirname, basename
from typing import Tuple, List
from rdflib import Graph

from rml.io.mapping_validator import MappingValidator
from rml.io import RML_RULES_SHAPE


class MappingValidatorTests(unittest.TestCase):
    def _validate_rules(self, path: str) -> None:
        rules = Graph().parse(path, format='turtle')
        mapping_validator = MappingValidator(RML_RULES_SHAPE)
        mapping_validator.validate(rules)

    def test_read_valid(self) -> None:
        p = 'tests/assets/io/mapping_files/validator_rules_valid.rml.ttl'
        self._validate_rules(p)

    def test_read_invalid(self) -> None:
        with self.assertRaises(ValueError):
            p = 'tests/assets/io/mapping_files/validator_rules_invalid.rml.ttl'
            self._validate_rules(p)

    def test_non_existing_mapping_rules(self) -> None:
        with self.assertRaises(FileNotFoundError):
            p = 'tests/assets/io/mapping_files/mapping_001.ttl'
            self._validate_rules(p)


if __name__ == '__main__':
    unittest.main(failfast=True)
