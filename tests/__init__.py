from http.server import SimpleHTTPRequestHandler

# Sources
from tests.sources.csv_source import CSVLogicalSourceTests
from tests.sources.logical_source import LogicalSourceTests
from tests.sources.json_source import JSONLogicalSourceTests
from tests.sources.xml_source import XMLLogicalSourceTests
from tests.sources.sql_source import SQLLogicalSourceTests
from tests.sources.sparql_source import SPARQLJSONLogicalSourceTests, SPARQLXMLLogicalSourceTests
from tests.sources.dcat_source import DCATLogicalSourceTests
from tests.sources.rdf_source import RDFLogicalSourceTests
from tests.sources.hydra_source import HydraLogicalSourceTests

# Maps
from tests.maps.subject_map import SubjectMapTests
from tests.maps.predicate_map import PredicateMapTests
from tests.maps.object_map import ObjectMapTests
from tests.maps.triples_map import TriplesMapTests

# io
from tests.io.mapping_reader import MappingReaderTests