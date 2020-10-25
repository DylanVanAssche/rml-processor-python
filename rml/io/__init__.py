from os.path import abspath


RML_RULES_SHAPE = abspath('rml/io/assets/rml_rules_shape.ttl')

# Expose classes at module level
from rml.io.mapping_compiler import MappingCompiler  # nopep8
from rml.io.mapping_validator import MappingValidator  # nopep8
from rml.io.mapping_reader import MappingReader  # nopep8
