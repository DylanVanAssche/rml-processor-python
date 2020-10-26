import sys
import docker
from logging import debug, info, error
from docker.types import Mount
import requests
from sqlalchemy import create_engine
from os import environ, getcwd
from time import sleep

# In CI environment, Docker-in-Docker is used.
# Docker containers are not running at host 'localhost' but 'docker'.
if environ.get('CI') is not None:
    environ['HOST'] = 'docker'
else:
    environ['HOST'] = 'localhost'

HOST = environ['HOST']
TIMEOUT = 30
CONNECTION_URL = '{dialect}://{username}:{password}@{host}:{port}/{database}'
MYSQL_IMAGE = 'mysql:8'
MYSQL_NAME = 'mysql-db'
MYSQL_PORTS = {'3306/tcp': 3306}
MYSQL_ENVIRONMENT = {'MYSQL_USER': 'root', 'MYSQL_ALLOW_EMPTY_PASSWORD': True,
                     'MYSQL_DATABASE': 'test'}
POSTGRESQL_IMAGE = 'postgres:12'
POSTGRESQL_NAME = 'postgresql-db'
POSTGRESQL_PORTS = {'5432/tcp': 5432}
POSTGRESQL_ENVIRONMENT = {'POSTGRES_USER': 'root',
                          'POSTGRES_HOST_AUTH_METHOD': 'trust',
                          'POSTGRES_DB': 'test'}
SQLSERVER_IMAGE = 'mcr.microsoft.com/mssql/server:2019-latest'
SQLSERVER_NAME = 'sqlserver-db'
SQLSERVER_PORTS = {'1433/tcp': 1433}
SQLSERVER_ENVIRONMENT = {'ACCEPT_EULA': 'Y',
                         'SA_PASSWORD': 'yourStrong(!)Password'}

SPARQL_IMAGE = 'atomgraph/fuseki'
SPARQL1_CMD = '--mem /ds1'
SPARQL1_NAME = 'sparql-resource1'
SPARQL1_PORTS = {'3030/tcp': 3031}
SPARQL1_PING = f'http://{HOST}:3031/ds1'
SPARQL2_CMD = '--mem /ds2'
SPARQL2_NAME = 'sparql-resource2'
SPARQL2_PORTS = {'3030/tcp': 3032}
SPARQL2_PING = f'http://{HOST}:3032/ds2'

DCAT_IMAGE = 'python:slim'
DCAT_NAME = 'dcat-resource'
DCAT_CMD = 'python -m http.server 8000'
DCAT_PORTS = {'8000/tcp': 8000}
DCAT_MOUNT = [Mount(target='/tests',
                    source=f'{getcwd()}/tests',
                    type='bind',
                    read_only=True)]
DCAT_PING = f'http://{HOST}:8000'

def setup_module():
    """
    Launch all the databases used in these tests through Docker containers.
    The required Docker images are automatically pulled from Docker Hub and
    configured.
    You need to be able access Docker without root and provide a working
    network connection.
    """
    # Intialize Docker client
    client = docker.from_env()
    debug('Docker client initialized')

    # Stop all containers
    for c in client.containers.list():
        if c.name in [MYSQL_NAME, POSTGRESQL_NAME, SQLSERVER_NAME, \
                SPARQL1_NAME, SPARQL2_NAME, DCAT_NAME]:
            c.stop()
            info(f'Stopped container: {c.name}')

    # Run MySQL database container
    client.containers.run(MYSQL_IMAGE, environment=MYSQL_ENVIRONMENT, remove=True,
                          auto_remove=True, detach=True, name=MYSQL_NAME,
                          ports=MYSQL_PORTS)
    debug('MySQL container started')
    environ['MYSQL_JDBC'] = CONNECTION_URL\
            .format(dialect='mysql+pymysql', username='root', password='',
                    host=HOST, port=3306, database='test')

    # Run PostgreSQL database container
    client.containers.run(POSTGRESQL_IMAGE, environment=POSTGRESQL_ENVIRONMENT,
                          remove=True, auto_remove=True, detach=True,
                          name=POSTGRESQL_NAME, ports=POSTGRESQL_PORTS)
    debug('PostgreSQL container started')
    environ['POSTGRESQL_JDBC'] = CONNECTION_URL\
            .format(dialect='postgresql+psycopg2', username='root', password='',
                    host=HOST, port=5432, database='test')

    # Run SQLServer database container
    client.containers.run(SQLSERVER_IMAGE, environment=SQLSERVER_ENVIRONMENT,
                          remove=True, auto_remove=True, detach=True,
                          name=SQLSERVER_NAME, ports=SQLSERVER_PORTS)
    debug('SQL Server container started')
    environ['SQLSERVER_JDBC'] = CONNECTION_URL\
            .format(dialect='mssql+pyodbc', username='sa',
                    password='yourStrong(!)Password', host=HOST,
                    port=1433, database='master') + '?driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1'

    # Run multiple Fuseki SPARQL resource container
    client.containers.run(SPARQL_IMAGE, command=SPARQL1_CMD, remove=True,
                          auto_remove=True, detach=True, name=SPARQL1_NAME,
                          ports=SPARQL1_PORTS)
    client.containers.run(SPARQL_IMAGE, command=SPARQL2_CMD, remove=True,
                          auto_remove=True, detach=True, name=SPARQL2_NAME,
                          ports=SPARQL2_PORTS)
    debug('Fuseki containers started')
    port1: str = '3031'
    port2: str = '3032'
    environ['SPARQL1_PORT'] = port1
    environ['SPARQL2_PORT'] = port2
    environ['SPARQL1_QUERY'] = f'http://{HOST}:{port1}/ds1/query'
    environ['SPARQL2_QUERY'] = f'http://{HOST}:{port2}/ds2/query'
    environ['SPARQL1_UPDATE'] = f'http://{HOST}:{port1}/ds1/update'
    environ['SPARQL2_UPDATE'] = f'http://{HOST}:{port2}/ds2/update'

    # Run DCAT HTTP server container
    client.containers.run(DCAT_IMAGE, command=DCAT_CMD, mounts=DCAT_MOUNT,
                          remove=True, auto_remove=True, detach=True,
                          name=DCAT_NAME, ports=DCAT_PORTS)
    debug('HTTP server container started')
    environ['DCAT_PORT'] = '8000'
    environ['DCAT_HOST'] = HOST

    # Block until all containers are up
    info(f'Waiting until all containers are ready...')
    ready = False
    for _ in range(TIMEOUT):
        up = []
        try:
            # Check MySQL
            engine = create_engine(environ['MYSQL_JDBC'])
            engine.connect().close()
            up.append('MySQL')

            # Check PostgreSQL
            engine = create_engine(environ['POSTGRESQL_JDBC'])
            engine.connect().close()
            up.append('PostgreSQL')

            # Check SQL Server
            engine = create_engine(environ['SQLSERVER_JDBC'])
            engine.connect().close()
            up.append('SQL Server')

            # Check Fuseki
            requests.get(SPARQL1_PING).raise_for_status()
            requests.get(SPARQL2_PING).raise_for_status()
            up.append('Fuseki')

            # Check DCAT
            requests.get(DCAT_PING).raise_for_status()
            up.append('HTTP server')

            ready = True
            break;
        except Exception as e:
            info(f'Not all containers are up ({up}), retrying in 1s...')
            up = []
            debug(e)
            sleep(1)

    # MS SQLSERVER doesn't allow to specify a default database in their Docker
    # image. Connect with 'master' as database and create 'test' database.
    engine = create_engine(environ['SQLSERVER_JDBC'])
    engine = engine.execution_options(isolation_level='AUTOCOMMIT')
    engine.execute('CREATE DATABASE TestDB;')
    debug('Initilization SQL Server complete')

    # Set JDBC connection string to 'test' database
    environ['SQLSERVER_JDBC'] = CONNECTION_URL.format(dialect='mssql+pyodbc',
            username='sa', password='yourStrong(!)Password', host=HOST,
            port=1433, database='TestDB') + '?driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1'

    # Exit tests when container initialization fails
    if not ready:
        error(f'Containers are not initialized after {TIMEOUT}s!')
        sys.exit(1)

def teardown_module():
    """
    Database containers are stopped as soon as all the tests are complete.
    """
    # Intialize Docker client
    client = docker.from_env()
    debug('Docker client initialized')

    # Stop all containers
    for c in client.containers.list():
        if c.name in [MYSQL_NAME, POSTGRESQL_NAME, SQLSERVER_NAME, \
                SPARQL1_NAME, SPARQL2_NAME, DCAT_NAME]:
            c.stop()
            info(f'Stopped container: {c.name}')

# Tests for sources
from tests.io.sources.logical_source import LogicalSourceTests
from tests.io.sources.csv_source import CSVLogicalSourceTests
from tests.io.sources.json_source import JSONLogicalSourceTests
from tests.io.sources.xml_source import XMLLogicalSourceTests
from tests.io.sources.sql_source import SQLLogicalSourceTests
from tests.io.sources.rdf_source import RDFLogicalSourceTests
from tests.io.sources.dcat_source import DCATLogicalSourceTests
from tests.io.sources.sparql_source import SPARQLXMLLogicalSourceTests, \
                                           SPARQLJSONLogicalSourceTests

# Tests for maps
from tests.io.maps.term_map import TermMapTests
from tests.io.maps.subject_map import SubjectMapTests
from tests.io.maps.predicate_map import PredicateMapTests
from tests.io.maps.object_map import ObjectMapTests
from tests.io.maps.triples_map import TriplesMapTests

# Tests for mappings and RML test cases
from tests.io.mapping_reader import MappingReaderTests
from tests.io.mapping_validator import MappingValidatorTests
from tests.io.mapping_compiler import MappingCompilerTests
from tests.io.rml_tc import RMLTestCasesTests

# Tests for targets
from tests.io.targets.logical_target import LogicalTargetTests
from tests.io.targets.stdout_target import StdoutLogicalTargetTests
from tests.io.targets.file_target import FileLogicalTargetTests
