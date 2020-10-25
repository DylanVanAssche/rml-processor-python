import unittest
import time
from shutil import copyfileobj
from parameterized import parameterized
from glob import glob
from os.path import abspath, join, isfile
from os import getcwd, chdir, environ
from typing import Tuple, List, Optional
from tempfile import NamedTemporaryFile
from rdflib import ConjunctiveGraph
from rdflib.term import URIRef, BNode
from rdflib.plugins.stores import sparqlstore
from rdflib.compare import to_isomorphic, graph_diff
from sqlalchemy import create_engine

from rml.io.mapping_reader import MappingReader
from rml.io.maps import TriplesMap

EXPECTED_TEST_FAILURES = ('RMLTC0002c-CSV',  #  Undefined column
                          'RMLTC0002c-MySQL',  #  Undefined column
                          'RMLTC0002c-PostgreSQL',  #  Undefined column
                          'RMLTC0002c-SQLServer',  #  Undefined column
                          'RMLTC0002e',  #  Undefined rr:tableName
                          'RMLTC0002f',  #  Delimited identifiers rr:template
                          'RMLTC0002g',  #  Invalid SQL query
                          'RMLTC0002h',  #  Duplicate column name in SQL SELECT
                          'RMLTC0003a',  #  Invalid/undefined SQL version
                          'RMLTC0004b',  #  SubjectMap rr:termType != rr:Literal
                          'RMLTC0007h',  #  Assign tiples to non-IRI named graph
                          'RMLTC0012c',  #  Missing rr:subjectMap
                          'RMLTC0012d',  #  2 rr:subjectMaps
                          'RMLTC0015b')  #  Invalid language tag
UNSUPPORTED_TEST_CASES = ('RMLTC0008b',  # Lack of RefObjectMap
                          'RMLTC0009a',  # Lack of joinCondition
                          'RMLTC0009b',  # Lack of joinCondition
                          'RMLTC0010c',  # RDFLib cannot parse \{
                          'RMLTC0011a',  # rr:logicalTable is not supported
                          'RMLTC0016b-SQLServer', # SQLServer float precision
                          'RMLTC0016d-MySQL',  # MySQL boolean is casted as tinyint
                          'RMLTC0016e-MySQL',  # Binary data issues
                          'RMLTC0016e-PostgreSQL',  # PostgresSQL binary
                          'RMLTC0016e-SQLServer',  # SQLServer binary
                          'RMLTC0018a-MySQL',  # CHAR spacing trimmed by SQLAlchemy
                          'RMLTC0019a',  # @base prefix is not supported
                          'RMLTC0019b',  # @base prefix is not supported
                          'RMLTC0020a',  # @base prefix is not supported
                          'RMLTC0020b')  # @base prefix is not supported
WORKING_DIR = getcwd()
TEST_CASES_DIR = 'tests/assets/rml-test-cases/test-cases/*'
TEST_CASES_RULES_NAME = 'mapping.ttl'
TEST_CASES_SQL_RESOURCE_NAME = 'resource.sql'
TEST_CASES_SPARQL1_RESOURCE_NAME = ['resource.ttl', 'resource1.ttl']
TEST_CASES_SPARQL2_RESOURCE_NAME = 'resource2.ttl'
TEST_CASES_EXPECTED_OUTPUT_NAME = 'output.nq'

class RMLTestCasesTests(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._port: Optional[int] = None

    def _process_tm_results(self, tm_list: List[TriplesMap], path: str) -> None:
        self.assertGreater(len(tm_list), 0)
        generated_triples = ConjunctiveGraph()
        for tm in tm_list:
            while True:
                try:
                    for t in next(tm):
                        # No Named Graph specified
                        if t[3] is None:
                            generated_triples.add(t)
                        else:
                            generated_triples.addN(t)
                except StopIteration:
                    break
        generated_triples = to_isomorphic(generated_triples)
        print('Generated triples:')
        for t in generated_triples.quads():
            print(t)

        p = join(path, TEST_CASES_EXPECTED_OUTPUT_NAME)
        expected_triples = ConjunctiveGraph()
        data = open(p, 'rb')
        expected_triples.parse(data, format='nquads')
        expected_triples = to_isomorphic(expected_triples)
        print('Expected triples:')
        for t in expected_triples.quads():
            print(t)
        if '0002h-SPARQL' in path:
            self.fail()

        self.assertEqual(generated_triples,
                         expected_triples,
                         msg='Difference:\n '
                         f'{graph_diff(generated_triples, expected_triples)}')

    @parameterized.expand([(p,) for p in sorted(glob(TEST_CASES_DIR))])
    def test_rml_test_cases(self, path: str) -> None:
        """
        Execute the RML test cases to see if our engine complies with the RML
        specification.
        """
        print(f'RML test case: {path}')

        # Change directory to current test
        chdir(WORKING_DIR)
        path = abspath(path)
        chdir(path)
        self.addCleanup(chdir, WORKING_DIR)

        is_sql: bool = False
        jdbc: str
        if 'MySQL' in path:
            print('Initializing MySQL database...')
            jdbc = environ['MYSQL_JDBC']
            is_sql = True

        if 'PostgreSQL' in path:
            print('Initializing PostgreSQL database...')
            jdbc = environ['POSTGRESQL_JDBC']
            is_sql = True

        if 'SQLServer' in path:
            print('Initializing SQLServer database...')
            jdbc = environ['SQLSERVER_JDBC']
            is_sql = True

        if 'SPARQL' in path:
            print('Initializing SPARQL endpoint 1...')
            # Connect to Fuseki store
            store1 = sparqlstore.SPARQLUpdateStore()
            store1.open((environ['SPARQL1_QUERY'], environ['SPARQL1_UPDATE']))

            # Clear the store
            for t in store1.triples((None, None, None)):
                triple = t[0]
                context = t[1]
                store1.remove(triple, context)

            # Read the resource test data
            g1 = ConjunctiveGraph()
            if isfile(TEST_CASES_SPARQL1_RESOURCE_NAME[0]):
                g1.parse(join(path, TEST_CASES_SPARQL1_RESOURCE_NAME[0]),
                        format='turtle')
            else:
                g1.parse(join(path, TEST_CASES_SPARQL1_RESOURCE_NAME[1]),
                        format='turtle')

            # RDFLib SPARQLStore doesn't like Blank Nodes, give them a subject.
            for t in g1.triples((None, None, None)):
                if isinstance(t[0], BNode):
                    s = URIRef(f'http://example.com/{t[0]}')
                else:
                    s = t[0]
                if isinstance(t[2], BNode):
                    o = URIRef(f'http://example.com/{t[2]}')
                else:
                    o = t[2]
                p = t[1]
                print(s, p, o)
                store1.add((s, p, o))

            # Disconnect
            store1.close()

            # Repeat for Fuseki store 2 if applicable
            if isfile(TEST_CASES_SPARQL2_RESOURCE_NAME):
                print('Initializing SPARQL endpoint 2...')
                store2 = sparqlstore.SPARQLUpdateStore()
                store2.open((environ['SPARQL2_QUERY'], environ['SPARQL2_UPDATE']))
                # Clear the store
                for t in store2.triples((None, None, None)):
                    triple = t[0]
                    context = t[1]
                    store2.remove(triple, context)
                g2 = ConjunctiveGraph()
                g2.parse(join(path, TEST_CASES_SPARQL2_RESOURCE_NAME),
                         format='turtle')
                for t in g2.triples((None, None, None)):
                    if isinstance(t[0], BNode):
                        s = URIRef(f'http://example.com/{t[0]}')
                    else:
                        s = t[0]
                    if isinstance(t[2], BNode):
                        o = URIRef(f'http://example.com/{t[2]}')
                    else:
                        o = t[2]
                    p = t[1]
                    print(s, p, o)
                    store2.add((s, p, o))
                store2.close()

        if is_sql:
            with open(TEST_CASES_SQL_RESOURCE_NAME, 'r') as f:
                statements: List[str] = f.read().strip(' \n').split(';')
                engine = create_engine(jdbc)
                autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
                if 'MySQL' in path:
                    autocommit_engine.execute('DROP DATABASE test;')
                    autocommit_engine.execute('CREATE DATABASE test;')
                if 'SQLServer' in path:
                    autocommit_engine.execute('USE master;')
                    autocommit_engine.execute('ALTER DATABASE TestDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;')
                    autocommit_engine.execute('USE master;')
                    autocommit_engine.execute('DROP DATABASE TestDB;')
                    autocommit_engine.execute('USE master;')
                    autocommit_engine.execute('CREATE DATABASE TestDB;')
                for s in filter(None, statements):
                    print(s)
                    autocommit_engine.execute(s)
                print('Test case SQL loaded')


        if any(f in path for f in UNSUPPORTED_TEST_CASES):
            self.skipTest(f'Unsupported test case: {path}')

        mapping_rules_path = join(path, TEST_CASES_RULES_NAME)

        # Replace CONNECTIONDSN and PORT variables
        with NamedTemporaryFile(mode='w+', delete=False) as tf:
            # Create a temporary copy and point to it
            with open(mapping_rules_path, 'r') as f:
                tf.write(f.read())
                tf.flush()
            mapping_rules_path = tf.name

            # Replace variables
            tf.seek(0)
            rules = tf.read()
            if 'MySQL' in path:
                rules = rules.replace('CONNECTIONDSN',
                                      environ['MYSQL_JDBC'])
            elif 'PostgreSQL' in path:
                rules = rules.replace('CONNECTIONDSN',
                                      environ['POSTGRESQL_JDBC'])
            elif 'SQLServer' in path:
                rules = rules.replace('CONNECTIONDSN',
                                      environ['SQLSERVER_JDBC'])
            elif 'SPARQL' in path:
                rules = rules.replace('http://localhost:PORT/ds1/sparql',
                                      environ['SPARQL1_QUERY'])
                rules = rules.replace('http://localhost:PORT/ds2/sparql',
                                      environ['SPARQL2_QUERY'])

            # Overide rules
            tf.seek(0)
            tf.truncate(0)
            tf.write(rules)
            tf.flush()

            # Test case should fail, check if exception is raised
            if any(f in path for f in EXPECTED_TEST_FAILURES):
                with self.assertRaises(Exception):
                    mapping_reader = MappingReader(mapping_rules_path)
                    tm_list = mapping_reader.resolve()
                    self._process_tm_results(tm_list, path)
            # Test case should not fail, check output
            else:
                mapping_reader = MappingReader(mapping_rules_path)
                tm_list = mapping_reader.resolve()
                print(mapping_rules_path)
                print(tm_list)
                self.assertTrue(tm_list)  # tm_list must contain at least 1 Triples Map
                self._process_tm_results(tm_list, path)

    def tear_down(self) -> None:
        # Restore working directory
        chdir(WORKING_DIR)


if __name__ == '__main__':
    unittest.main(failfast=True)
