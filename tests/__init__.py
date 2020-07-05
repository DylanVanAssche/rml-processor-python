# Sources
from tests.io.sources.logical_source import LogicalSourceTests
from tests.io.sources.json_source import JSONLogicalSourceTests
from tests.io.sources.xml_source import XMLLogicalSourceTests
from tests.io.sources.sql_source import SQLLogicalSourceTests
from tests.io.sources.rdf_source import RDFLogicalSourceTests
from tests.io.sources.dcat_source import DCATLogicalSourceTests
from tests.io.sources.hydra_source import HydraLogicalSourceTests
from tests.io.sources.sparql_source import SPARQLXMLLogicalSourceTests, \
                                           SPARQLJSONLogicalSourceTests

# Maps
from tests.io.maps.subject_map import SubjectMapTests
from tests.io.maps.predicate_map import PredicateMapTests
from tests.io.maps.object_map import ObjectMapTests
from tests.io.maps.triples_map import TriplesMapTests

# io
from tests.io.mapping_reader import MappingReaderTests
