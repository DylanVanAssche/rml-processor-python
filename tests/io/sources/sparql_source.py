#!/usr/bin/env python

import unittest

from rml.namespace.xmls import SPARQL_RESULTS_PREFIX, SPARQL_RESULTS_NS
from rml.io.sources import SPARQLJSONLogicalSource, SPARQLXMLLogicalSource, \
                           MIMEType

SPARQL_QUERY = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?actor ?name WHERE {
        ?tvshow rdf:type dbo:TelevisionShow.
        ?tvshow rdfs:label "Friends"@en.
        ?tvshow dbo:starring ?actor.
        ?actor foaf:name ?name
    }
"""
SPARQL_DUPLICATE_VAR_QUERY = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?actor ?actor ?name WHERE {
        ?tvshow rdf:type dbo:TelevisionShow.
        ?tvshow rdfs:label "Friends"@en.
        ?tvshow dbo:starring ?actor.
        ?actor foaf:name ?name
    }
"""
SPARQL_ASK_QUERY = """
    PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
    ASK  { ?x foaf:name  "Alice" }
"""
NS = { SPARQL_RESULTS_PREFIX: SPARQL_RESULTS_NS }


class SPARQLJSONLogicalSourceTests(unittest.TestCase):
    def test_mime_type(self) -> None:
        """
        Test the MIME type property
        """
        source = SPARQLJSONLogicalSource('$.results.bindings.[*].actor',
                                         'http://dbpedia.org/sparql',
                                         SPARQL_QUERY)
        self.assertEqual(source.mime_type, MIMEType.JSON)

    def test_iterator_single_value(self) -> None:
        """
        Test if we can iterate over the results of the JSONPath expression
        """
        source = SPARQLJSONLogicalSource('$.results.bindings.[*].actor',
                                         'http://dbpedia.org/sparql',
                                         SPARQL_QUERY)
        self.assertDictEqual(next(source),
                             {
                                 'type' : 'uri',
                                 'value' : 'http://dbpedia.org/resource/Jennifer_Aniston'
                             })
        self.assertDictEqual(next(source),
                             {
                                 'type' : 'uri',
                                 'value' : 'http://dbpedia.org/resource/David_Schwimmer'
                             })
        self.assertDictEqual(next(source),
                             {
                                 'type' : 'uri',
                                 'value' : 'http://dbpedia.org/resource/Lisa_Kudrow'
                             })
        self.assertDictEqual(next(source),
                             {
                                 'type' : 'uri',
                                 'value' : 'http://dbpedia.org/resource/Matt_LeBlanc'
                             })
        self.assertDictEqual(next(source),
                             {
                                 'type' : 'uri',
                                 'value' : 'http://dbpedia.org/resource/Matthew_Perry'
                             })
        self.assertDictEqual(next(source),
                             {
                                 'type' : 'uri',
                                 'value' : 'http://dbpedia.org/resource/Courteney_Cox'
                             })
        with self.assertRaises(StopIteration):
            next(source)

    def test_non_existing_endpoint(self) -> None:
        """
        Test if we raise a FileNotFoundError exception when the endpoint does
        not exist
        """
        with self.assertRaises(FileNotFoundError):
            source = SPARQLJSONLogicalSource('$.results.bindings.[*].actor.value',
                                             'http://dbpedia.org/empty',
                                             SPARQL_QUERY)

    def test_duplicate_variables(self) -> None:
        """
        Test if we raise a ValueError exception when the SPARQL query contains
        duplicate variables.
        """
        with self.assertRaises(ValueError):
            source = SPARQLJSONLogicalSource('$.results.bindings.[*]',
                                            'http://dbpedia.org/sparql',
                                            SPARQL_DUPLICATE_VAR_QUERY)

    def test_missing_select(self) -> None:
        """
        Test if we raise a ValueError exception when the SPARQL query does not
        contain a SELECT statement.
        """
        with self.assertRaises(ValueError):
            source = SPARQLXMLLogicalSource('$.results.bindings.[*]',
                                            'http://dbpedia.org/sparql',
                                            SPARQL_ASK_QUERY)

    def test_invalid_jsonpath(self) -> None:
        """
        Test if we raise a ValueError when the JSONPath expression is invalid
        """
        with self.assertRaises(ValueError):
            source = SPARQLJSONLogicalSource('&$"£*W$',
                                             'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)

    def test_empty_iterator(self) -> None:
        """
        Test if we handle an empty iterator
        """
        with self.assertRaises(StopIteration):
            source = SPARQLJSONLogicalSource('$.empty',
                                             'http://dbpedia.org/sparql',
                                             SPARQL_QUERY)
            next(source)

class SPARQLXMLLogicalSourceTests(unittest.TestCase):
    def test_mime_type(self) -> None:
        """
        Test the MIME type property
        """
        source = SPARQLXMLLogicalSource('//sr:result/sr:binding[@name="actor"]',
                                        'http://dbpedia.org/sparql',
                                        SPARQL_QUERY)
        self.assertEqual(source.mime_type, MIMEType.TEXT_XML)

    def test_iterator(self) -> None:
        """
        Test if we can iterate over the results of the XPath expression
        """
        source = SPARQLXMLLogicalSource('//sr:result/sr:binding[@name="actor"]',
                                        'http://dbpedia.org/sparql',
                                        SPARQL_QUERY)
        actor = next(source)
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].tag,
                         '{http://www.w3.org/2005/sparql-results#}uri')
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].text,
                         'http://dbpedia.org/resource/Jennifer_Aniston')

        actor = next(source)
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].tag,
                         '{http://www.w3.org/2005/sparql-results#}uri')
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].text,
                         'http://dbpedia.org/resource/David_Schwimmer')

        actor = next(source)
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].tag,
                         '{http://www.w3.org/2005/sparql-results#}uri')
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].text,
                         'http://dbpedia.org/resource/Lisa_Kudrow')

        actor = next(source)
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].tag,
                         '{http://www.w3.org/2005/sparql-results#}uri')
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].text,
                         'http://dbpedia.org/resource/Matt_LeBlanc')

        actor = next(source)
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].tag,
                         '{http://www.w3.org/2005/sparql-results#}uri')
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].text,
                         'http://dbpedia.org/resource/Matthew_Perry')

        actor = next(source)
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].tag,
                         '{http://www.w3.org/2005/sparql-results#}uri')
        self.assertEqual(actor.xpath('./sr:uri', namespaces = NS)[0].text,
                         'http://dbpedia.org/resource/Courteney_Cox')

        with self.assertRaises(StopIteration):
            next(source)

    def test_non_existing_endpoint(self) -> None:
        """
        Test if we raise a FileNotFoundError exception when the endpoint does
        not exist
        """
        with self.assertRaises(FileNotFoundError):
            source = SPARQLXMLLogicalSource('/sparql/results/result/binding',
                                            'http://dbpedia.org/empty',
                                            SPARQL_QUERY)

    def test_duplicate_variables(self) -> None:
        """
        Test if we raise a ValueError exception when the SPARQL query contains
        duplicate variables.
        """
        with self.assertRaises(ValueError):
            source = SPARQLXMLLogicalSource('/sr:sparql',
                                            'http://dbpedia.org/sparql',
                                            SPARQL_DUPLICATE_VAR_QUERY)

    def test_missing_select(self) -> None:
        """
        Test if we raise a ValueError exception when the SPARQL query does not
        contain a SELECT statement.
        """
        with self.assertRaises(ValueError):
            source = SPARQLXMLLogicalSource('/sr:sparql',
                                            'http://dbpedia.org/sparql',
                                            SPARQL_ASK_QUERY)

    def test_invalid_xpath(self) -> None:
        """
        Test if we raise a ValueError when the XPath expression is invalid
        """
        with self.assertRaises(ValueError):
            source = SPARQLXMLLogicalSource('&$"£*W$',
                                            'http://dbpedia.org/sparql',
                                            SPARQL_QUERY)

    def test_empty_iterator(self) -> None:
        """
        Test if we handle an empty iterator
        """
        with self.assertRaises(StopIteration):
            source = SPARQLXMLLogicalSource('/empty',
                                            'http://dbpedia.org/sparql',
                                            SPARQL_QUERY)
            next(source)

if __name__ == '__main__':
    unittest.main()
