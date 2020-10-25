#!/usr/bin/env python

import re
import sys
import datetime
import argparse
from os import path
from rdflib import Graph
from rdflib.term import URIRef, BNode, Literal
from rdflib.plugins.serializers.turtle import TurtleSerializer
from rdflib import plugin
from typing import IO, Optional, List, Dict, Any, Union
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import OperationalError, ArgumentError

from rml.namespace import XSD, RDF, R2RML, RML, D2RQ
from rml.io.maps import TriplesMap, SubjectMap, PredicateMap, ObjectMap, \
                        PredicateObjectMap

URITEMPLATE_PATTERN = re.compile(r'\{(.*?)\}')


class TurtleWithPrefixes(TurtleSerializer):
    """
    A turtle serializer that always emits prefixes
    Workaround for https://github.com/RDFLib/rdflib/issues/1048
    """
    roundtrip_prefixes = True  # Undocumented, forces to write all prefixes


class MappingCompiler():
    def __init__(self) -> None:
        super().__init__()
        # Register TurtleWithPrefixes serializer as 'tortoise' format
        plugin.register('tortoise',
                        plugin.Serializer,
                        'rml.io.mapping_compiler',
                        'TurtleWithPrefixes')

    def compile(self, rules: Graph) -> Graph:
        """
        Compiles the provided mapping rules.
        This compiler reduces the effort that the processor needs to do during
        the processing of mapping rules which should result in less bugs and a
        better performance.
        """

        # Compile
        rules = self._expand_shortcuts(rules)
        rules = self._strip_jdbc(rules)
        rules = self._rewrite_rr_table_name(rules)
        rules = self._add_natural_sql_datatypes(rules)
        rules = self._rewrite_rr_graph_map(rules)
        rules = self._rewrite_rr_class(rules)
        return rules

    def _expand_shortcuts(self, rules: Graph) -> Graph:
        """
        Expands R2RML and RML shortcuts.
        The following shortcuts are expanded:
            - rr:subject <subject> to rr:subjectMap [
                                        rr:constant <subject>
                                      ]
            - rr:predicate <predicate> to rr:predicateMap [
                                            rr:constant <predicate>
                                          ]
            - rr:object <object> to rr:objectMap [
                                      rr:constant <object>
                                    ]
            - rr:graph <graph> to rr:graphMap [
                                      rr:constant <graph>
                                    ]
        TODO: languageMap, see Gitlab #30. datatypeMap is proposed!
        """
        # 1. rr:subject expansion
        for t in rules.triples((None, R2RML.subject, None)):
            tm, _, s = t
            sm = BNode()
            rules.add((tm, R2RML.subjectMap, sm))
            rules.add((sm, R2RML.constant, s))
            rules.add((sm, R2RML.termType, R2RML.IRI))
            rules.remove(t)

        # 2. rr:predicate expansion
        for t in rules.triples((None, R2RML.predicate, None)):
            pom, _, p = t
            pm = BNode()
            rules.add((pom, R2RML.predicateMap, pm))
            rules.add((pm, R2RML.constant, p))
            rules.add((pm, R2RML.termType, R2RML.IRI))
            rules.remove(t)

        # 3. rr:object expansion
        for t in rules.triples((None, R2RML.object, None)):
            pom, _, o = t
            om = BNode()
            rules.add((pom, R2RML.objectMap, om))
            rules.add((om, R2RML.constant, o))
            rules.add((om, R2RML.termType, R2RML.IRI))
            rules.remove(t)

        # 4. rr:graph expansion
        for t in rules.triples((None, R2RML.graph, None)):
            pom, _, g = t
            gm = BNode()
            rules.add((pom, R2RML.graphMap, gm))
            rules.add((gm, R2RML.constant, g))
            rules.add((gm, R2RML.termType, R2RML.IRI))
            rules.remove(t)

        return rules

    def _strip_jdbc(self, rules: Graph) -> Graph:
        for t in rules.triples((None, R2RML.predicateObjectMap, None)):
            tm, _, pom = t

            # Get Logical Source
            ls = rules.value(subject=tm, predicate=RML.logicalSource)
            rml_source = rules.value(ls, RML.source)
            rml_source_type = rules.value(rml_source, RDF.type)

            # Logical Source is not a D2RQ Database, skip
            if rml_source_type != D2RQ.Database:
                print(f'{rml_source} is not a D2RQ Database, skip')
                continue
            d2rq_jdbc: str = str(rules.value(rml_source, D2RQ.jdbcDSN))
            d2rq_jdbc = d2rq_jdbc.lstrip('jdbc:')  # Strip jdbc
            rules.set((rml_source, D2RQ.jdbcDSN, Literal(d2rq_jdbc)))
        return rules

    def _rewrite_rr_table_name(self, rules: Graph) -> Graph:
        """
        Rewrite rr:tableName as rml:query.
        This results in less code paths and tests since there's only 1 way to
        achieve this goal. Moreover, columns that are not used in the mapping
        rules are not fetched.

        1. The table name and column names referenced in the mapping rules are
           retrieved.
        2. The retrieved table and columns names are used to create a SQL
           query. rr:tableName is replaced by the new SQL query as rml:query.
        """
        tm_list: Dict[str, Any] = {}

        # 1. Extract rr:tableName and the referenced column names
        for t in rules.triples((None, R2RML.predicateObjectMap, None)):
            tm, _, pom = t

            # Get Logical Source
            ls = rules.value(subject=tm, predicate=RML.logicalSource)
            rml_source = rules.value(ls, RML.source)
            rml_source_type = rules.value(rml_source, RDF.type)

            # Logical Source is not a D2RQ Database, skip
            if rml_source_type != D2RQ.Database:
                print(f'{rml_source} is not a D2RQ Database, skip')
                continue

            tm_id = str(tm)
            if tm_id not in tm_list:
                tm_list[tm_id] = {
                    'source': None,
                    'columns': [],
                    'jdbc': ''
                }
            tm_list[tm_id]['source'] = ls

            # Find SQL table name
            rr_table_name = rules.value(ls, R2RML.tableName)

            if rr_table_name is None:
                print(f'No rr:tableName found in Logical Source: {ls}')
                continue

            # Get all possible column names
            d2rq_jdbc = str(rules.value(rml_source, D2RQ.jdbcDSN))
            tm_list[tm_id]['jdbc'] = d2rq_jdbc
            engine = create_engine(tm_list[tm_id]['jdbc'])
            inspector = inspect(engine)
            column_list = [c['name'] for c in
                           inspector.get_columns(rr_table_name)]

            # Find column names for rr:SubjectMap, rr:PredicateMap and
            # rr:ObjectMap
            om = rules.value(subject=pom, predicate=R2RML.objectMap)
            tm_list[tm_id]['columns'] += self._get_column_names(rules, om)
            pm = rules.value(subject=pom, predicate=R2RML.predicateMap)
            tm_list[tm_id]['columns'] += self._get_column_names(rules, pm)
            sm = rules.value(subject=tm, predicate=R2RML.subjectMap)
            tm_list[tm_id]['columns'] += self._get_column_names(rules, sm)

            # Remove duplicates
            tm_list[tm_id]['columns'] = list(set(tm_list[tm_id]['columns']))

        # 2. Build SQL query and replace rr:tableName with rml:query
        for tm in tm_list:
            tm_id = str(tm)
            rml_query = rules.value(tm_list[tm_id]['source'], RML.query)

            if rml_query is not None:
                print('rml:query is already provided, not overiding it with '
                      'rr:tableName constructed query!')
                continue

            # Build SQL query
            query: str = 'SELECT '
            rr_table_name = rules.value(tm_list[tm_id]['source'],
                                        R2RML.tableName)
            if tm_list[tm_id]['columns']:
                for c in tm_list[tm_id]['columns']:
                    c.replace(' ', '\\ ')  # Escape spaces in column names
                    query += c
                    # No comma for the last column name
                    if c == tm_list[tm_id]['columns'][-1]:
                        query += ' '
                    else:
                        query += ', '
                query += f'FROM {rr_table_name};'
                print('Extracted query: ' + query)
            # No tables extracted, fall back to R2RML specification
            else:
                query += f'* FROM {rr_table_name}'
                print(f'WARNING: No columns extracted for TriplesMap {tm}! '
                      'Falling back to SELECT * FROM <table_name>')

            # Add rml:query
            rules.add((tm_list[tm_id]['source'],
                       RML.query,
                       Literal(query)))
            # Remove rr:tableName
            rules.remove((tm_list[tm_id]['source'],
                          R2RML.tableName,
                          rr_table_name))
            print('Query converted to: '
                  f'{rules.value(tm_list[tm_id]["source"], RML.query)}')

        return rules

    def _rewrite_rr_graph_map(self, rules: Graph) -> Graph:
        """
        Rewrite rr:graph into rr:graphMap.
        This avoids a separate handling of rr:graph to reduce the possible code
        paths and tests. Furthermore, the processor does not have to check if a
        Named Graph was defined in the SubjectMap or PredicateObjectMap since
        it's only used from now on in PredicateObjectMaps.

        1. Find all rr:graphMaps. Non-expanded shortcuts will be expanded!
        2. Move any rr:graphMap from SubjectMap to the PredicateObjectMaps
           which do not have a rr:graphMap.
        """
        # 1. Find rr:graphMap in SubjectMaps
        for t1 in rules.triples((None, R2RML.subjectMap, None)):
            tm, _, sm = t1
            graph = rules.value(subject=sm, predicate=R2RML.graphMap)
            if graph is not None:
                # 2. Move rr:graphMap to PredicateObjectMaps if not overiden
                for t2 in rules.triples((tm, R2RML.predicateObjectMap, None)):
                    _, _, pom = t2
                    overide = rules.value(subject=pom,
                                          predicate=R2RML.graphMap)
                    if overide is None:
                        rules.add((pom, R2RML.graphMap, graph))
                rules.remove((sm, R2RML.graphMap, graph))

        return rules

    def _rewrite_rr_class(self, rules: Graph) -> Graph:
        """
        Rewrite rr:class in a SubjectMap to a new PredicateObjectMap with
        rdf:type as predicate.
        By removing this edge case, the code path of SubjectMap can be heavily
        reduced to resolving a rml:reference or rr:template

        1. Find rr:class and remove it from the SubjectMap.
        2. Create a new PredicateObjectMap with rdf:type as predicate.
        3. Associate the new PredicateObjectMap with the SubjectMap.
        """
        for t in rules.triples((None, R2RML['class'], None)):  # keyword
            # Find to which SubjectMap and TriplesMap with an associated
            # rr:class
            subject_map, _, rr_class = t
            triples_map = rules.value(None, R2RML.subjectMap, subject_map)

            # Create PredicateObjectMap with rdf:type and rr:class value
            pom = BNode()
            pm = BNode()
            om = BNode()
            rules.add((pm, R2RML.constant, RDF.type))
            rules.add((om, R2RML.constant, rr_class))
            rules.add((pom, R2RML.predicateMap, pm))
            rules.add((pom, R2RML.objectMap, om))
            rules.add((triples_map, R2RML.predicateObjectMap, pom))

            # Remove rr:class from SubjectMap
            rules.remove(t)

        return rules

    def _add_natural_sql_datatypes(self, rules: Graph) -> Graph:
        """
        Add the natural SQL datatypes to the mapping rules.
        The R2RML specification requires that processors map the natural SQL
        datatypes to the XSD namespace as explained in section 10.2.

        1. The referenced column names are inspected to retrieve the datatype
           of each column.
        2. The SQL datatype is translated into a datatype of the XSD
           namespace.
        3. For each one, rr:datatype is added to the ObjectMap.


        Note: rr:object doesn't need to be handled since rr:object can never
        refer to a SQL column since it only can contain an rr:constant value
        """

        for t in rules.triples((None, R2RML.objectMap, None)):
            pom, _, om = t
            # Get SQL database Logical Source
            tm = rules.value(predicate=R2RML.predicateObjectMap, object=pom)
            ls = rules.value(subject=tm, predicate=RML.logicalSource)
            rml_source = rules.value(ls, RML.source)
            rml_source_type = rules.value(rml_source, RDF.type)

            # Logical Source is not a D2RQ Database, skip
            if rml_source_type != D2RQ.Database:
                print(f'{rml_source} is not a D2RQ Database, skip')
                continue

            # Find SQL database query and column information
            query: str = rules.value(ls, RML.query)
            d2rq_jdbc = rules.value(rml_source, D2RQ.jdbcDSN)
            _columns: List[str] = self._get_column_names(rules, om,
                                                         no_iri=True)
            _columns = [c.strip('\"').strip('`').strip('[').strip(']')
                        for c in _columns]

            # Multiple columns result into multiple data types which is
            # impossible.
            if len(_columns) != 1:
                print('WARNING: Unable to determine datatype with multiple '
                      f'columns: {_columns}')
                continue
            column = _columns[0]

            # Access database to find datatype
            try:
                with create_engine(d2rq_jdbc).connect() as connection:
                    result = connection.execute(query).first()
                    if result is None:
                        print(f'WARNING: {query} returned 0 rows, skipping')
                        continue
                    result = dict(result)
                    datatype = self._get_xsd_datatype(result[column])
            except KeyError as e:
                print(f'WARNING: Column doesn\'t exist: {e}')
                continue
            except (OperationalError, ArgumentError) as e:
                raise ValueError(f'WARNING: Unable to execute SQL query: {e}')

            # Add datatypes when not provided
            overide = rules.value(om, R2RML.datatype)
            language_tag = rules.value(om, R2RML.language)
            language_map = rules.value(om, RML.languageMap)
            if datatype is not None and overide is None and \
                    language_tag is None and language_map is None:
                rules.add((om, R2RML.datatype, datatype))

        return rules

    def _get_column_names(self, rules: Graph, subject: Union[URIRef, BNode],
                          no_iri: bool = False) -> List[str]:
        columns: List[str] = []

        # Handle rml:reference
        ref = rules.value(subject, RML.reference)
        if ref is not None:
            columns = [str(ref)]
        # Handle rr:template
        else:
            temp = rules.value(subject, R2RML.template)
            if temp is not None:
                temp = str(temp)
                # If needed, filter IRIs out of the column list.
                # We don't want to add SQL datatypes to IRIs
                if (temp.startswith('http://') or temp.startswith('https://'))\
                        and no_iri:
                    return []
                variables: List[str] = URITEMPLATE_PATTERN.findall(temp)
                for v in variables:
                    columns.append(v)

        return columns

    def _get_xsd_datatype(self, value: Any) \
            -> Optional[URIRef]:  # pragma: no cover
        # Enable coverage again when switched to pyodbc and all RML test cases
        # regarding SQL datatypes are passing
        """
        Converts SQL datatypes into datatypes from the XSD namespace.
        Follow section 10.2 of the R2RML specification.

        SQLAlchemy converts the SQL datatypes already in Python datatypes.
        Because of this, the conversion happens using Python datatypes instead
        of SQL datatypes.
        """
        instance = type(value)
        if instance is bytes:
            return XSD.hexBinary
        # DECIMAL and FLOAT are both casted to float by Python
        elif instance is float:
            return XSD.double
        elif instance is int:
            return XSD.integer
        elif instance is bool:
            return XSD.boolean
        elif instance is datetime.date:
            return XSD.date
        elif instance is datetime.time:
            return XSD.time
        elif instance is datetime.datetime:
            return XSD.dateTime
        # STRING does not get a datatype
        else:
            return None


if __name__ == '__main__':  # pragma: no cover
    p = argparse.ArgumentParser(description='Compiles RML mapping rules')
    p.add_argument('mapping', type=str, help='Mapping rules Turtle file')
    p.add_argument('destination', type=str, help='Location to write the '
                   'compiled mapping rules as Turtle.')
    # Arguments parsing
    args = p.parse_args()
    if not path.exists(args.mapping):
        print(f'Ooops! {args.mapping} file path does not exist!')
        sys.exit(1)

    # Read mapping rules
    rules = Graph()
    rules.parse(args.mapping, format='turtle')

    # Compile
    c = MappingCompiler()
    rules = c.compile(rules)

    # Write mapping rules
    rules.serialize(destination=args.destination, format='tortoise')
