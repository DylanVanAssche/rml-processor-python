#!/usr/bin/env python

import unittest

from rml.io.sources import SPARQLJSONLogicalSource, SPARQLXMLLogicalSource

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

class SPARQLJSONLogicalSourceTests(unittest.TestCase):
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
    def test_iterator(self) -> None:
        """
        Test if we can iterate over the results of the XPath expression
        """
        source = SPARQLXMLLogicalSource('//result/binding[@name="actor"]',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
        actor = next(source)
        self.assertEqual(actor.xpath('./uri')[0].tag, 'uri')
        self.assertEqual(actor.xpath('./uri')[0].text,
                         'http://dbpedia.org/resource/Jennifer_Aniston')

        actor = next(source)
        self.assertEqual(actor.xpath('./uri')[0].tag, 'uri')
        self.assertEqual(actor.xpath('./uri')[0].text,
                         'http://dbpedia.org/resource/David_Schwimmer')

        actor = next(source)
        self.assertEqual(actor.xpath('./uri')[0].tag, 'uri')
        self.assertEqual(actor.xpath('./uri')[0].text,
                         'http://dbpedia.org/resource/Lisa_Kudrow')

        actor = next(source)
        self.assertEqual(actor.xpath('./uri')[0].tag, 'uri')
        self.assertEqual(actor.xpath('./uri')[0].text,
                         'http://dbpedia.org/resource/Matt_LeBlanc')

        actor = next(source)
        self.assertEqual(actor.xpath('./uri')[0].tag, 'uri')
        self.assertEqual(actor.xpath('./uri')[0].text,
                         'http://dbpedia.org/resource/Matthew_Perry')

        actor = next(source)
        self.assertEqual(actor.xpath('./uri')[0].tag, 'uri')
        self.assertEqual(actor.xpath('./uri')[0].text,
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
