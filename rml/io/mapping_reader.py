from rdflib import Graph
from rdflib.term import URIRef, Literal, BNode
from typing import List, Optional, Union

from rml.io.sources import LogicalSource, CSVLogicalSource, \
                           JSONLogicalSource, XMLLogicalSource, \
                           RDFLogicalSource, DCATLogicalSource, \
                           HydraLogicalSource, SQLLogicalSource, \
                           SPARQLXMLLogicalSource, SPARQLJSONLogicalSource, \
                           MIMEType
from rml.io.targets import LogicalTarget
from rml.io.maps import TriplesMap, PredicateObjectMap, SubjectMap, \
                        ObjectMap, PredicateMap, TermType
from rml.namespace import RML, R2RML, RDF, QL, D2RQ, SD, CSVW, DCAT, HYDRA, \
                          FORMATS
from rml.io import MappingValidator
from rml.io import RML_RULES_SHAPE


class MappingReader:
    def __init__(self, path: str) -> None:
        """
        Creates a MappingReader to read RML rules
        """
        self._graph: Graph = Graph()
        self._path: str = path
        self._validator: MappingValidator = MappingValidator(RML_RULES_SHAPE)
        self._read()

    def _read(self) -> None:
        """
        Reads RML rules in the Turtle format.
        """
        try:
            rules = self._graph.parse(self._path, format='turtle')
        except FileNotFoundError:
            raise FileNotFoundError(f'Unable to open {self._path}')
        except Exception:
            raise ValueError(f'Unable to parse {self._path} as Turtle')

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
        return tm_list

    def _resolve_triples_map(self, tm: URIRef) -> TriplesMap:
        print(f'Triples Map: {tm}')

        # Logical Source
        ls_list = []
        for ls in self._graph.objects(tm, RML.logicalSource):
            ls_list.append(self._resolve_logical_source(ls))

        mime_type: MIMEType = ls_list[0].mime_type

        # Subject Map
        sm_list = []
        for subject_map in self._graph.objects(tm, R2RML.subjectMap):
            sm_list.append(self._resolve_subject_map(subject_map, mime_type))

        if not sm_list:  # no rr:subjectMap, check for rr:subject
            for subject in self._graph.objects(tm, R2RML.subject):
                sm_list.append(self._resolve_subject(subject, mime_type))

        # Predicate Object Maps
        pom_list = []
        for pred_obj_map in self._graph.objects(tm,
                                                R2RML.predicateObjectMap):
            pom = self._resolve_predicate_object_map(pred_obj_map, mime_type)
            pom_list.append(pom)

        resolved_tm: TriplesMap = TriplesMap(ls_list[0], sm_list[0], pom_list)
        print('-' * 80)

        return resolved_tm

    def _resolve_logical_source(self, ls: URIRef) -> LogicalSource:
        print(f'Logical Source: {ls}')
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

        print(f'\tSource: {rml_source}')
        print(f'\tType: {rml_source_type}')
        print(f'\tReference formulation: {rml_reference_formulation}')
        print(f'\tIterator: {rml_iterator}')
        print(f'\tQuery: {rml_query}')

        # Local file
        if rml_source_type is None:
            # CSV file
            if rml_reference_formulation == QL.CSV:
                print('Local CSV file')
                # CSVW dialect support (https://www.w3.org/ns/csvw) is limited
                # to:
                # - csvw:delimiter (Dialect.delimiter)
                # - csvw:doubleQuote (Dialect.doublequote)
                # - csvw:quoteChar (Dialect.quotechar)
                # - csvw:skipInitialSpace (Dialect.skipinitialspace)
                # - csvw:encoding (open statement 'encoding')
                #
                # Other dialect options of CSVW are not supported by the
                # Python CSV module:
                # - csvw:header: a header is required in all cases.
                # - csvw:headerRowCount: not supported by Python's CSV module.
                # - csvw:lineTerminators: not supported by Python's CSV module.
                # - csvw:skipColumns: not supported by Python's CSV module.
                # - csvw:skipRows: not supported by Python's CSV module.
                # - csvw:trim: not supported by this processor yet.
                # - csvw:skipBlankRows: not supported by this processor yet.
                csvw_dialect: URIRef = self._graph.value(_rml_source,
                                                         CSVW.dialect)
                csvw_delimiter: str = ','
                csvw_double_quote: bool = False
                csvw_quote_char: str = '"'
                csvw_skip_initial_space: bool = False
                csvw_encoding: str = 'utf-8'

                if csvw_dialect is not None:
                    csvw_delimiter = \
                        str(self._graph.value(csvw_dialect, CSVW.delimiter,
                                              default=csvw_delimiter))
                    csvw_double_quote = \
                        bool(self._graph.value(csvw_dialect,
                                               CSVW.doubleQuote,
                                               default=csvw_double_quote))
                    csvw_quote_char = \
                        str(self._graph.value(csvw_dialect, CSVW.quoteChar,
                                              default=csvw_quote_char))
                    csvw_skip_initial_space = \
                        self._graph.value(csvw_dialect,
                                          CSVW.skipInitialSpace,
                                          default=csvw_skip_initial_space)
                    csvw_skip_initial_space = bool(csvw_skip_initial_space)
                    csvw_encoding = str(self._graph.value(csvw_dialect,
                                                          CSVW.encoding,
                                                          default='utf-8'))

                print(f'\tDelimiter: {csvw_delimiter}')
                print(f'\tDouble quote enabled: {csvw_double_quote}')
                print(f'\tQuote char: {csvw_quote_char}')
                print(f'\tSkip initial space: {csvw_skip_initial_space}')

                # FIXME: Support more CSV dialect options, see Gitlab issue #35
                if csvw_double_quote or csvw_quote_char == '"' or \
                        csvw_skip_initial_space or csvw_encoding != 'utf-8':
                    print('WARNING: Only limited CSV dialect support is '
                          'implemented, see Gitlab issue #35')

                return CSVLogicalSource(rml_source, csvw_delimiter)
            # JSON file
            elif rml_reference_formulation == QL.JSONPath:
                print('Local JSON file')
                return JSONLogicalSource(rml_iterator, rml_source)
            # XML file
            elif rml_reference_formulation == QL.XPath:
                print('Local XML file')
                return XMLLogicalSource(rml_iterator, rml_source)
            # Unknown local file
            else:
                raise NotImplementedError('Unknown RML reference formulation: '
                                          '{rml_reference_formulation}')
        # SQL database
        elif rml_source_type == D2RQ.Database:
            print('SQL database')
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
            print(f'\tSQL version: {rr_sql_version}')
            print(f'\tJDBC DSN: {d2rq_jdbc_DSN}')
            print(f'\tJDBC driver: {d2rq_jdbc_driver}')
            print(f'\tUsername: {d2rq_username}')
            print(f'\tPassword: {d2rq_password}')
            # FIXME: SQL database access is not completely implemented, see
            # Gitlab issue #36
            if d2rq_username is not None or d2rq_password is not None or \
                    d2rq_jdbc_driver is not None:
                print('WARNING: Only limited SQL database access is '
                      'supported, see Gitlab issue #36')
            return SQLLogicalSource(d2rq_jdbc_DSN, query=rml_query.toPython())
        # SPARQL endpoint
        elif rml_source_type == SD.Service:
            print('SPARQL endpoint')
            sd_endpoint: str = self._graph.value(rml_source,
                                                 SD.endpoint).toPython()
            sd_supported_language: URIRef = \
                self._graph.value(rml_source, SD.supportedLanguage)
            sd_result_format: URIRef = self._graph.value(rml_source,
                                                         SD.resultFormat)
            print(f'\tEndpoint: {sd_endpoint}')
            print(f'\tSupported language: {sd_supported_language}')
            print(f'\tResult format: {sd_result_format}')

            # FIXME: Warn when SPARQL 1.0 is required, setting the SPARQL
            # version is not possible at the moment, see Gitlab issue #37
            if sd_supported_language != SD.SPARQL11Query:  # pragma: no cover
                print('WARNING: SPARQL supported language is ignored! See '
                      'Gitlab issue #37')

            if sd_result_format == FORMATS.SPARQL_Results_JSON:
                return SPARQLJSONLogicalSource(rml_iterator,
                                               sd_endpoint,
                                               rml_query.toPython())
            elif sd_result_format == FORMATS.SPARQL_Results_XML:
                return SPARQLXMLLogicalSource(rml_iterator,
                                              sd_endpoint,
                                              rml_query.toPython())
            else:
                raise NotImplementedError('SPARQL results format not '
                                          'implemented, see Gitlab issue #31')
        # DCAT dataset
        elif rml_source_type == DCAT.Dataset:
            print('DCAT dataset')
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
                raise NotImplementedError('DCAT Dataset MIME type '
                                          '{_dcat_media_type} is not '
                                          'supported')
            print(f'DCAT distribution: {dcat_distribution}')
            print(f'DCAT download URL: {dcat_download_url}')
            print(f'DCAT media type: {dcat_media_type}')
            # If no RML iterator is provided, an RML query is provided for
            # iterating over RDF sources
            if rml_iterator == '':
                rml_iterator = rml_query
            return DCATLogicalSource(dcat_download_url, dcat_media_type,
                                     rml_iterator)
        else:
            raise ValueError(f'Unknown Logical Source description: {ls}')

    def _resolve_predicate_object_map(self, pom: URIRef, mime_type: MIMEType) \
            -> PredicateObjectMap:
        print(f'Predicate Object Map: {pom}')

        # Predicate Map
        pm_list = []
        for predicate_map in self._graph.objects(pom, R2RML.predicateMap):
            pm_list.append(self._resolve_predicate_map(predicate_map,
                                                       mime_type))

        if not pm_list:  # no rr:predicateMap, check for rr:predicate
            for predicate in self._graph.objects(pom, R2RML.predicate):
                pm_list.append(self._resolve_predicate(predicate, mime_type))

        # Object Map
        om_list = []
        for object_map in self._graph.objects(pom, R2RML.objectMap):
            om_list.append(self._resolve_object_map(object_map, mime_type))

        if not om_list:  # no rr:objectMap, check for rr:object
            for object in self._graph.objects(pom, R2RML.object):
                om_list.append(self._resolve_object(object, mime_type))

        return PredicateObjectMap(pm_list[0], om_list[0])

    def _resolve_subject_map(self, sm: URIRef,
                             mime_type: MIMEType) -> SubjectMap:
        print(f'Subject Map: {sm}')

        rr_template = self._graph.value(sm, R2RML.template)
        rml_reference = self._graph.value(sm, RML.reference)
        rr_constant: URIRef = self._graph.value(sm, R2RML.constant)
        rr_class: URIRef = self._graph.value(sm, R2RML['class'])  # keyword

        print(f'\tTemplate: {rr_template}')
        print(f'\tReference: {rml_reference}')
        print(f'\tConstant: {rr_constant}')
        print(f'\tClass: {rr_class}')

        if rr_template is not None:
            return SubjectMap(rr_template.toPython(),
                              TermType.TEMPLATE, mime_type)
        elif rml_reference is not None:
            return SubjectMap(rml_reference.toPython(),
                              TermType.REFERENCE, mime_type)
        elif rr_constant is not None:
            return SubjectMap(rr_constant, TermType.CONSTANT, mime_type)
        else:  # pragma: no cover
            raise ValueError(f'Unable to resolve rr:subjectMap {sm}, should '
                             'be catched by shape validation. Report this as '
                             'an issue!')

    def _resolve_subject(self, s: URIRef, mime_type: MIMEType) -> SubjectMap:
        print(f'Subject Map shortcut: {s}')
        print(f'\tConstant: {s}')
        return SubjectMap(s, TermType.CONSTANT, mime_type)

    def _resolve_object_map(self, om: URIRef, mime_type: MIMEType) \
            -> ObjectMap:
        print(f'\tObject Map: {om}')
        rr_template = self._graph.value(om, R2RML.template)
        rml_reference = self._graph.value(om, RML.reference)
        rr_constant = self._graph.value(om, R2RML.constant)
        rr_term_type = self._graph.value(om, R2RML.termType)
        rr_language = self._graph.value(om, R2RML.language)
        rr_datatype = self._graph.value(om, R2RML.datatype)

        print(f'\t\tTemplate: {rr_template}')
        print(f'\t\tReference: {rml_reference}')
        print(f'\t\tConstant: {rr_constant}')
        print(f'\t\tTerm type: {rr_term_type}')

        # No term type specified? Literal by default if one of the conditions
        # are true:
        # - has rml:reference
        # - has rr:language
        # - has rr:datatype
        # See the RML spec (https://rml.io/spec) for a detailed explanation.
        if rr_template is not None:
            if rr_term_type == R2RML.IRI:
                return ObjectMap(rr_template.toPython(), TermType.TEMPLATE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype)
            elif rr_term_type == R2RML.Literal:
                return ObjectMap(rr_template.toPython(), TermType.TEMPLATE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype, is_iri=False)
            elif rr_term_type == R2RML.BlankNode:
                raise NotImplementedError('Blank nodes are not supported yet')
            elif rr_language is not None or rr_datatype is not None:
                return ObjectMap(rr_template.toPython(), TermType.TEMPLATE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype, is_iri=False)
            else:
                return ObjectMap(rr_template.toPython(), TermType.TEMPLATE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype)
        elif rml_reference is not None:
            # Term type specifies IRI
            if rr_term_type == R2RML.IRI:
                return ObjectMap(rml_reference.toPython(), TermType.REFERENCE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype)
            elif rr_term_type == R2RML.BlankNode:
                raise NotImplementedError('Blank nodes are not supported yet')
            elif rr_term_type == R2RML.Literal:
                return ObjectMap(rml_reference.toPython(), TermType.REFERENCE,
                                 mime_type,
                                 language=rr_language, datatype=rr_datatype,
                                 is_iri=False)
            else:
                return ObjectMap(rml_reference.toPython(), TermType.REFERENCE,
                                 mime_type, language=rr_language,
                                 datatype=rr_datatype, is_iri=False)
        elif rr_constant is not None:
            return ObjectMap(rr_constant, TermType.CONSTANT, mime_type)
        else:  # pragma: no cover
            raise ValueError('ObjectMap requires at least 1 rr:template, '
                             'rml:reference or rr:constant. Should be catched '
                             'by shape validation, report this as an issue!')

    def _resolve_object(self, o: URIRef, mime_type: MIMEType) -> ObjectMap:
        print(f'\tObject: {o}')
        print(f'\t\tConstant: {o}')
        return ObjectMap(o, TermType.CONSTANT, mime_type)

    def _resolve_predicate_map(self, pm: URIRef, mime_type: MIMEType) \
            -> PredicateMap:
        print(f'\tPredicate Map: {pm}')
        rr_template: Literal = self._graph.value(pm, R2RML.template)
        rml_reference: Literal = self._graph.value(pm, RML.reference)
        rr_constant: URIRef = self._graph.value(pm, R2RML.constant)

        print(f'\t\tTemplate: {rr_template}')
        print(f'\t\tReference: {rml_reference}')
        print(f'\t\tConstant: {rr_constant}')

        if rr_template is not None:
            return PredicateMap(rr_template.toPython(), TermType.CONSTANT,
                                mime_type)
        elif rml_reference is not None:
            return PredicateMap(rml_reference.toPython(), TermType.CONSTANT,
                                mime_type)
        elif rr_constant is not None:
            return PredicateMap(rr_constant, TermType.CONSTANT, mime_type)
        else:  # pragma: no cover
            raise ValueError(f'Unable to resolved rr:predicateMap {pm}. '
                             'Should be catched by shape validation, report'
                             'this as an issue!')

    def _resolve_predicate(self, p: URIRef, mime_type: MIMEType) \
            -> PredicateMap:
        print(f'\tPredicate: {p}')
        print(f'\t\tConstant: {p}')
        return PredicateMap(p, TermType.CONSTANT, mime_type)
