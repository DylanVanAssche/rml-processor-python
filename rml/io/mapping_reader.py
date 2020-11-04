from logging import debug, info, warning, error, critical
from itertools import product
from rdflib import Graph
from rdflib.term import URIRef, Literal, BNode, Identifier
from typing import List, Optional, Union, Dict

from rml.io.sources import LogicalSource, CSVLogicalSource, \
                           JSONLogicalSource, XMLLogicalSource, \
                           RDFLogicalSource, DCATLogicalSource, \
                           SQLLogicalSource, SPARQLXMLLogicalSource, \
                           SPARQLJSONLogicalSource, MIMEType, CSVColumn, \
                           CSVWTrimMode
from rml.io.targets import LogicalTarget
from rml.io.maps import TriplesMap, PredicateObjectMap, SubjectMap, \
                        ObjectMap, PredicateMap, ReferenceType
from rml.namespace import RML, R2RML, RDF, QL, D2RQ, SD, CSVW, DCAT, HYDRA, \
                          FORMATS
from rml.io import MappingValidator, MappingCompiler
from rml.io import RML_RULES_SHAPE


class MappingReader:
    def __init__(self, path: str) -> None:
        """
        Creates a MappingReader to read RML rules
        """
        self._graph: Graph = Graph()
        self._path: str = path
        self._validator: MappingValidator = MappingValidator(RML_RULES_SHAPE)
        self._compiler: MappingCompiler = MappingCompiler()
        self._read()
        self._validator.validate(self.rules)
        self._compiler.compile(self.rules)

    def _read(self) -> None:
        """
        Reads RML rules in the Turtle format.
        """
        try:
            rules = self._graph.parse(self._path, format='turtle')
        except FileNotFoundError:
            msg = f'Unable to open {self._path}'
            critical(msg)
            raise FileNotFoundError(msg)
        except Exception as e:
            msg = f'Unable to parse {self._path} as Turtle: {e}'
            critical(msg)
            raise ValueError(msg)

    @property
    def rules(self) -> Graph:
        return self._graph

    def resolve(self) -> List[TriplesMap]:
        """
        Resolve RML rules into Python objects
        """
        tm_list: List[TriplesMap] = []
        for tm in self._graph.subjects(predicate=RDF.type,
                                       object=R2RML.TriplesMap):
            tm_list.append(self._resolve_triples_map(tm))
            info(f'Resolved TriplesMap: {tm}')
        return tm_list

    def _resolve_triples_map(self, tm: URIRef) -> TriplesMap:
        info(f'Triples Map: {tm}')

        # Logical Source
        ls_list: List[LogicalSource] = []
        for ls in self._graph.objects(tm, RML.logicalSource):
            ls_list.append(self._resolve_logical_source(ls))

        mime_type: MIMEType = ls_list[0].mime_type

        # Subject Map
        sm_list: List[SubjectMap] = []
        for subject_map in self._graph.objects(tm, R2RML.subjectMap):
            sm_list.append(self._resolve_subject_map(subject_map, mime_type))
        info(f'Resolved SubjectMaps: {sm_list}')

        # Predicate Object Maps
        pom_list: List[PredicateObjectMap] = []
        for pred_obj_map in self._graph.objects(tm,
                                                R2RML.predicateObjectMap):
            pom_list += self._resolve_predicate_object_map(pred_obj_map,
                                                           mime_type)
        info(f'Resolved PredicateObjectMaps: {pom_list}')

        resolved_tm: TriplesMap = TriplesMap(ls_list[0], sm_list[0], pom_list)
        debug('-' * 80)

        return resolved_tm

    def _resolve_logical_source(self, ls: URIRef) -> LogicalSource:
        info(f'Logical Source: {ls}')

        rml_source_type: URIRef = None
        _rml_source = self._graph.value(ls, RML.source)
        rml_source: Union[str, URIRef]

        # Convert Literal to string (local file Logical Source)
        if isinstance(_rml_source, Literal):
            rml_source = _rml_source.toPython()  # Convert Literal to Python
            rml_source_type = None  # Local file
        # Detect the correct Logical Source type if URIRef or BNode
        elif self._graph.value(_rml_source, RDF.type) == CSVW.Table:
            rml_source = self._graph.value(_rml_source, CSVW.url)
            rml_source_type = None
        else:
            rml_source = _rml_source  # No conversion needed
            rml_source_type = self._graph.value(_rml_source, RDF.type)

        rml_reference_formulation: URIRef = \
            self._graph.value(ls, RML.referenceFormulation)
        _rml_iterator: Literal = self._graph.value(ls, RML.iterator)
        rml_iterator: str = ''
        if _rml_iterator is not None:
            rml_iterator = _rml_iterator.toPython()
        rml_query: Literal = self._graph.value(ls, RML.query)
        rr_table_name: Literal = self._graph.value(ls, R2RML.tableName)

        debug(f'\tSource: {rml_source}')
        debug(f'\tType: {rml_source_type}')
        debug(f'\tReference formulation: {rml_reference_formulation}')
        debug(f'\tIterator: {rml_iterator}')
        debug(f'\tQuery: {rml_query}')
        debug(f'\tTable Name: {rr_table_name}')

        # Local file
        if rml_source_type is None:
            # CSV file
            if rml_reference_formulation == QL.CSV:
                debug('Local CSV file')
                csvw_dialect: URIRef = self._graph.value(_rml_source,
                                                         CSVW.dialect)
                csvw_table_schema: URIRef = self._graph.value(_rml_source,
                                                              CSVW.tableSchema)
                config: Dict = {}

                # Handle CSVW dialects
                if csvw_dialect is not None:
                    debug('CSVW:Dialect')
                    csvw_delimiter: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.delimiter)
                    csvw_double_quote: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.doubleQuote)
                    csvw_quote_char: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.quoteChar)
                    csvw_skip_initial_space: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.skipInitialSpace)
                    csvw_encoding: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.encoding)
                    csvw_line_terminators: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.lineTerminators)
                    csvw_trim_mode: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.trim)
                    csvw_skip_columns: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.skipColumns)
                    csvw_skip_rows: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.skipRows)
                    csvw_comment_prefix: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.commentPrefix)
                    csvw_escape_char: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.escapeChar)
                    csvw_has_header: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.header)
                    csvw_header_row_count: Optional[Identifier] = \
                        self._graph.value(csvw_dialect, CSVW.headerRowCount)

                    debug(f'\tDelimiter: {csvw_delimiter}')
                    debug(f'\tDouble quote enabled: {csvw_double_quote}')
                    debug(f'\tQuote char: {csvw_quote_char}')
                    debug(f'\tSkip initial space: {csvw_skip_initial_space}')
                    debug(f'\tEncoding: {csvw_encoding}')
                    debug(f'\tLine terminators: {csvw_line_terminators}')
                    debug(f'\tTrim mode: {csvw_trim_mode}')
                    debug(f'\tSkipping first {csvw_skip_columns} columns')
                    debug(f'\tSkipping first {csvw_skip_rows} rows')
                    debug(f'\tComment prefix: {csvw_comment_prefix}')
                    debug(f'\tEscape character: {csvw_escape_char}')
                    debug(f'\tHas header: {csvw_has_header}')
                    debug(f'\tHeader row count: {csvw_header_row_count}')

                    # Build dynamic arguments based on the specified CSVW
                    # properties. Unspecified properties will get a default
                    # value in the CSV Logical Source
                    if csvw_delimiter is not None:
                        config['delimiter'] = csvw_delimiter.toPython()
                    if csvw_double_quote is not None:
                        config['double_quote'] = csvw_double_quote.toPython()
                    if csvw_quote_char is not None:
                        config['quote_char'] = csvw_quote_char.toPython()
                    if csvw_skip_initial_space is not None:
                        config['skip_initial_space'] = \
                                csvw_skip_initial_space.toPython()
                    if csvw_encoding is not None:
                        config['encoding'] = csvw_encoding.toPython()
                    if csvw_line_terminators is not None:
                        config['line_terminators'] = \
                                csvw_line_terminators.toPython()
                    if csvw_trim_mode is not None:
                        mode: Union[str, bool] = csvw_trim_mode.toPython()
                        # CSVW:trim can be provided as bool
                        if isinstance(mode, bool):
                            if mode:
                                config['trim_mode'] = \
                                        CSVWTrimMode.START_AND_END
                            else:
                                config['trim_mode'] = CSVWTrimMode.NONE
                        # Or as string with more fine grade control
                        else:
                            if mode == 'start':
                                config['trim_mode'] = CSVWTrimMode.START
                            elif mode == 'end':
                                config['trim_mode'] = CSVWTrimMode.END
                            elif mode == 'true':
                                config['trim_mode'] = \
                                        CSVWTrimMode.START_AND_END
                            elif mode == 'false':
                                config['trim_mode'] = CSVWTrimMode.NONE
                            else:  # pragma: no cover - fallback for validator
                                msg = f'Unknown CSVW trim: {mode}. This should'
                                ' be catched by the validator, report '
                                'this as an issue!'
                                critical(msg)
                                raise ValueError(msg)
                    if csvw_skip_columns is not None:
                        config['skip_columns'] = csvw_skip_columns.toPython()
                    if csvw_skip_rows is not None:
                        config['skip_rows'] = csvw_skip_rows.toPython()
                    if csvw_comment_prefix is not None:
                        config['comment_prefix'] = \
                                csvw_comment_prefix.toPython()
                    if csvw_escape_char is not None:
                        config['escape_char'] = csvw_escape_char.toPython()
                    if csvw_has_header is not None:
                        config['has_header'] = csvw_has_header.toPython()
                    if csvw_header_row_count is not None:
                        config['header_row_count'] = \
                                csvw_header_row_count.toPython()
                    # If no csvw:headerRowCount is provided, but csvw:header is
                    # set to True, csvw:headerRowCount is set to 1
                    # If False, csvw:headerRowCount is set to 0
                    elif 'has_header' in config:
                        if config['has_header']:
                            config['header_row_count'] = 1
                        else:
                            config['header_row_count'] = 0

                # Handle CSVW provided header
                if csvw_table_schema is not None:
                    debug('CSVW:TableSchema')
                    csvw_columns: URIRef = self._graph.value(csvw_table_schema,
                                                             CSVW.columns)
                    # csvw:columns contains an ordered list (rdf:List)
                    columns: List[CSVColumn] = []
                    for column in self._graph.items(csvw_columns):
                        name: str = \
                            self._graph.value(column, CSVW.name).toPython()
                        null_value: Optional[str] = \
                            self._graph.value(column, CSVW.null)
                        if null_value is not None:
                            columns.append(CSVColumn(name, null_value))
                        # If null value is not provided, fallback to default
                        else:
                            warning('CSVW:null missing, falling back to '
                                    'default')
                            columns.append(CSVColumn(name))

                        debug(f'\tName: {name}')
                        debug(f'\tNull value: {null_value}')
                    config['header'] = columns

                info(f'CSVW header & dialect configuration: {config}')

                # Expand config dictionary to arguments
                return CSVLogicalSource(rml_source, **config)
            # JSON file
            elif rml_reference_formulation == QL.JSONPath:
                debug('Local JSON file')
                return JSONLogicalSource(rml_iterator, rml_source)
            # XML file
            elif rml_reference_formulation == QL.XPath:
                debug('Local XML file')
                return XMLLogicalSource(rml_iterator, rml_source)
            # Unknown local file
            else:  # pragma: no cover
                msg = 'Unknown RML reference formulation: '
                f'{rml_reference_formulation}'
                critical(msg)
                raise NotImplementedError(msg)
        # SQL database
        elif rml_source_type == D2RQ.Database:
            debug('SQL database')
            rr_sql_version: URIRef = self._graph.value(ls, R2RML.sqlVersion)
            d2rq_jdbc_DSN: str = self._graph.value(rml_source,
                                                   D2RQ.jdbcDSN).toPython()
            d2rq_jdbc_DSN = d2rq_jdbc_DSN.replace('jdbc:', '')  # Drop 'jdbc:'
            d2rq_jdbc_driver: str = \
                self._graph.value(rml_source, D2RQ.jdbcDriver).toPython()
            d2rq_username: Optional[Literal] = \
                self._graph.value(rml_source, D2RQ.username)
            d2rq_password: Optional[Literal] = \
                self._graph.value(rml_source, D2RQ.password)
            if d2rq_username is not None:
                d2rq_username = d2rq_username.toPython()
            if d2rq_password is not None:
                d2rq_password = d2rq_password.toPython()
            debug(f'\tSQL version: {rr_sql_version}')
            debug(f'\tJDBC DSN: {d2rq_jdbc_DSN}')
            debug(f'\tJDBC driver: {d2rq_jdbc_driver}')
            debug(f'\tUsername: {d2rq_username}')
            debug(f'\tPassword: {d2rq_password}')
            # FIXME: SQL database access is not completely implemented, see
            # Gitlab issue #36
            if d2rq_username is not None or d2rq_password is not None or \
                    d2rq_jdbc_driver is not None:
                warning('Only limited SQL database access is supported, see '
                        'Gitlab issue #36')

            # Mapping validator enforces rr:tableName or rml:query
            # Mapping compiler translates rr:tableName to rml:query
            return SQLLogicalSource(d2rq_jdbc_DSN, query=rml_query.toPython())

        # SPARQL endpoint
        elif rml_source_type == SD.Service:
            debug('SPARQL endpoint')
            sd_endpoint: str = self._graph.value(rml_source,
                                                 SD.endpoint).toPython()
            sd_supported_language: URIRef = \
                self._graph.value(rml_source, SD.supportedLanguage)
            sd_result_format: URIRef = self._graph.value(rml_source,
                                                         SD.resultFormat)
            debug(f'\tEndpoint: {sd_endpoint}')
            debug(f'\tSupported language: {sd_supported_language}')
            debug(f'\tResult format: {sd_result_format}')

            if sd_supported_language != SD.SPARQL11Query:  # pragma: no cover
                error(f'{sd_supported_language} is not supported. Only'
                      'SPARQL 1.1 is supported.')

            if sd_result_format == FORMATS.SPARQL_Results_JSON:
                return SPARQLJSONLogicalSource(rml_iterator,
                                               sd_endpoint,
                                               rml_query.toPython())
            elif sd_result_format == FORMATS.SPARQL_Results_XML:
                return SPARQLXMLLogicalSource(rml_iterator,
                                              sd_endpoint,
                                              rml_query.toPython())
            else:  # pragma: no cover
                msg = 'SPARQL results format not implemented, see Gitlab '
                'issue #31'
                critical(msg)
                raise NotImplementedError(msg)
        # DCAT dataset
        elif rml_source_type == DCAT.Dataset:
            debug('DCAT dataset')
            dcat_distribution: Union[URIRef, BNode] = \
                self._graph.value(_rml_source, DCAT.distribution)
            dcat_download_url: str = \
                self._graph.value(dcat_distribution,
                                  DCAT.downloadURL).toPython()
            _dcat_media_type: str = \
                self._graph.value(dcat_distribution, DCAT.mediaType).toPython()
            try:
                dcat_media_type = MIMEType(_dcat_media_type)
                # Needs to be changed anyway, see
                # https://gitlab.com/dylanvanassche/rml-blocks/-/issues/42
            except ValueError:  # pragma: no cover
                msg = f'DCAT Dataset MIME type {_dcat_media_type} is not '
                'supported'
                critical(msg)
                raise NotImplementedError(msg)
            debug(f'DCAT distribution: {dcat_distribution}')
            debug(f'DCAT download URL: {dcat_download_url}')
            debug(f'DCAT media type: {dcat_media_type}')
            # If no RML iterator is provided, an RML query is provided for
            # iterating over RDF sources
            if rml_iterator == '':
                rml_iterator = rml_query
            return DCATLogicalSource(dcat_download_url, dcat_media_type,
                                     rml_iterator)
        else:  # pragma: no cover
            msg = f'Unknown Logical Source description: {ls}. This '
            'should be catched by the shape validation! Report this as an '
            'issue!'
            critical(msg)
            raise ValueError(msg)

    def _resolve_predicate_object_map(self, pom: URIRef, mime_type: MIMEType) \
            -> List[PredicateObjectMap]:
        debug(f'Predicate Object Map: {pom}')

        # Predicate Map
        pm_list = []
        for predicate_map in self._graph.objects(pom, R2RML.predicateMap):
            pm_list.append(self._resolve_predicate_map(predicate_map,
                                                       mime_type))
        debug(f'PredicateMaps: {pm_list}')

        # Object Map
        om_list = []
        for object_map in self._graph.objects(pom, R2RML.objectMap):
            om_list.append(self._resolve_object_map(object_map, mime_type))
        debug(f'ObjectMaps: {om_list}')

        pom_list: List[PredicateObjectMap] = []
        for pm, om in product(pm_list, om_list):
            pom_list.append(PredicateObjectMap(pm, om))

        return pom_list

    def _resolve_subject_map(self, sm: URIRef,
                             mime_type: MIMEType) -> SubjectMap:
        debug(f'Subject Map: {sm}')

        rr_template = self._graph.value(sm, R2RML.template)
        rml_reference = self._graph.value(sm, RML.reference)
        rr_constant: URIRef = self._graph.value(sm, R2RML.constant)
        rr_reference_type: Identifier = self._graph.value(sm, R2RML.termType)

        debug(f'\tTemplate: {rr_template}')
        debug(f'\tReference: {rml_reference}')
        debug(f'\tConstant: {rr_constant}')
        debug(f'\tTerm type: {rr_reference_type}')

        if rr_template is not None:
            return SubjectMap(rr_template.toPython(), ReferenceType.TEMPLATE,
                              mime_type, rr_reference_type)
        elif rml_reference is not None:
            return SubjectMap(rml_reference.toPython(),
                              ReferenceType.REFERENCE, mime_type,
                              rr_reference_type)
        elif rr_constant is not None:
            return SubjectMap(rr_constant, ReferenceType.CONSTANT, mime_type,
                              rr_reference_type)
        else:  # pragma: no cover
            msg: str = f'Unable to resolve rr:subjectMap {sm}, should be '
            'catched by shape validation. Report this as an issue!'
            critical(msg)
            raise ValueError(msg)

    def _resolve_object_map(self, om: URIRef, mime_type: MIMEType) \
            -> ObjectMap:
        debug(f'\tObject Map: {om}')
        rr_template = self._graph.value(om, R2RML.template)
        rml_reference = self._graph.value(om, RML.reference)
        rr_constant = self._graph.value(om, R2RML.constant)
        rr_reference_type = self._graph.value(om, R2RML.termType)
        rr_language = self._graph.value(om, R2RML.language)
        rr_datatype = self._graph.value(om, R2RML.datatype)

        debug(f'\t\tTemplate: {rr_template}')
        debug(f'\t\tReference: {rml_reference}')
        debug(f'\t\tConstant: {rr_constant}')
        debug(f'\t\tTerm type: {rr_reference_type}')

        # No term type specified? Literal by default if one of the conditions
        # are true:
        # - has rml:reference
        # - has rr:language
        # - has rr:datatype
        # See the RML spec (https://rml.io/spec) for a detailed explanation.
        if rr_template is not None:
            if rr_reference_type == R2RML.Literal or rr_language is not None\
                    or rr_datatype is not None:
                return ObjectMap(rr_template.toPython(),
                                 ReferenceType.TEMPLATE, mime_type,
                                 language=rr_language, datatype=rr_datatype,
                                 is_iri=False)
            elif rr_reference_type == R2RML.BlankNode:  # pragma: no cover
                msg = 'Blank nodes are not fully supported yet'
                critical(msg)
                raise NotImplementedError(msg)
            # R2RML.IRI or no rr:termType
            else:
                return ObjectMap(rr_template.toPython(),
                                 ReferenceType.TEMPLATE, mime_type,
                                 language=rr_language, datatype=rr_datatype,
                                 is_iri=True)
        elif rml_reference is not None:
            # Term type specifies IRI
            if rr_reference_type == R2RML.IRI:
                return ObjectMap(rml_reference.toPython(),
                                 ReferenceType.REFERENCE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype, is_iri=True)
            elif rr_reference_type == R2RML.BlankNode:  # pragma: no cover
                msg = 'Blank nodes are not fully supported yet'
                critical(msg)
                raise NotImplementedError(msg)
            # R2RML.Literal or has language tag or has datatype or no
            # rr:termType
            else:
                return ObjectMap(rml_reference.toPython(),
                                 ReferenceType.REFERENCE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype, is_iri=False)
        elif rr_constant is not None:
            if rr_reference_type == R2RML.Literal or rr_language is not None\
                    or rr_datatype is not None:
                return ObjectMap(rr_constant, ReferenceType.CONSTANT,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype, is_iri=False)
            else:
                return ObjectMap(rr_constant, ReferenceType.CONSTANT,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype, is_iri=True)
        else:  # pragma: no cover
            msg = 'ObjectMap requires at least 1 rr:template, '
            'rml:reference or rr:constant. Should be catched by shape '
            'validation, report this as an issue!'
            critical(msg)
            raise ValueError(msg)

    def _resolve_predicate_map(self, pm: URIRef, mime_type: MIMEType) \
            -> PredicateMap:
        debug(f'\tPredicate Map: {pm}')
        rr_template: Literal = self._graph.value(pm, R2RML.template)
        rml_reference: Literal = self._graph.value(pm, RML.reference)
        rr_constant: URIRef = self._graph.value(pm, R2RML.constant)

        debug(f'\t\tTemplate: {rr_template}')
        debug(f'\t\tReference: {rml_reference}')
        debug(f'\t\tConstant: {rr_constant}')

        if rr_template is not None:
            return PredicateMap(rr_template.toPython(), ReferenceType.TEMPLATE,
                                mime_type)
        elif rml_reference is not None:
            return PredicateMap(rml_reference.toPython(),
                                ReferenceType.REFERENCE, mime_type)
        elif rr_constant is not None:
            return PredicateMap(rr_constant, ReferenceType.CONSTANT, mime_type)
        else:  # pragma: no cover
            msg = f'Unable to resolved rr:predicateMap {pm}. '
            'Should be catched by shape validation, report'
            'this as an issue!'
            critical(msg)
            raise ValueError(msg)
