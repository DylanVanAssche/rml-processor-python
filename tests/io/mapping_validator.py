import unittest
from parameterized import parameterized
from glob import glob
from os.path import dirname, basename
from typing import Tuple, List
from rdflib import Graph

from rml.io.mapping_validator import MappingValidator
from rml.io import RML_RULES_SHAPE

# RMLTC0004b has invalid rr:termType for rr:subjectMap (rr:Literal)
EXPECTED_SHAPE_FAILURES = ('RMLTC0004b', )
# RMLTC0010c has special characters in template which cannot be parsed by
# rdflib
SKIPPED_SHAPE_FAILURES = ('RMLTC0010c', )

def load_rml_test_cases() -> List[Tuple]:
    test_cases: List[str] = glob('tests/assets/rml-test-cases/test-cases/*/mapping.ttl')
    rules: List[Tuple] = []

    for mapping_file in test_cases:
        rules.append((basename(dirname(mapping_file)), mapping_file))
    rules.sort()
    return rules

class MappingValidatorTests(unittest.TestCase):
    def test_read_valid(self) -> None:
        path = 'tests/assets/io/mapping_files/validator_rules_valid.rml.ttl'
        rules = Graph().parse(path, format='turtle')
        mapping_validator = MappingValidator(RML_RULES_SHAPE)
        mapping_validator.validate(rules)

    def test_read_invalid(self) -> None:
        with self.assertRaises(ValueError):
            path = 'tests/assets/io/mapping_files/validator_rules_invalid.rml.ttl'
            rules = Graph().parse(path, format='turtle')
            mapping_validator = MappingValidator(RML_RULES_SHAPE)
            mapping_validator.validate(rules)

    def test_non_existing_mapping_rules(self) -> None:
        with self.assertRaises(FileNotFoundError):
            path = 'tests/assets/io/mapping_files/mapping_001.ttl'
            rules = Graph().parse(path, format='turtle')
            mapping_validator = MappingValidator('/this/file/does/not/exist')
            mapping_validator.validate(rules)

    @parameterized.expand(load_rml_test_cases)
    def test_rml_rules_from_rml_test_cases(self, name: str, path: str) -> None:
        mapping_validator = MappingValidator(RML_RULES_SHAPE)
        try:
            rules = Graph().parse(path, format='turtle')
            mapping_validator.validate(rules, print_report=False)
        except Exception:
            if name.split('-')[0] in SKIPPED_SHAPE_FAILURES:
                self.skipTest(f'{name} skipped')

            self.assertTrue(name.split('-')[0] in EXPECTED_SHAPE_FAILURES,
                            f'RML test case {name} should pass!')


if __name__ == '__main__':
    unittest.main(failfast=True)
