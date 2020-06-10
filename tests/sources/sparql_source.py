#!/usr/bin/env python

import unittest

from rml.sources import SPARQLLogicalSource

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

class SPARQLLogicalSourceTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None

    def test_iterator(self) -> None:
        """
        Test if we can iterate over the results of the JSONPath expression
        """
        self.source = SPARQLLogicalSource('$.[*].actor.value',
                                          'http://dbpedia.org/sparql',
                                          SPARQL_QUERY)
        self.assertEqual(next(self.source), 'http://dbpedia.org/resource/Jennifer_Aniston')
        self.assertEqual(next(self.source), 'http://dbpedia.org/resource/David_Schwimmer')
        self.assertEqual(next(self.source), 'http://dbpedia.org/resource/Lisa_Kudrow')
        self.assertEqual(next(self.source), 'http://dbpedia.org/resource/Matt_LeBlanc')
        self.assertEqual(next(self.source), 'http://dbpedia.org/resource/Matthew_Perry')
        self.assertEqual(next(self.source), 'http://dbpedia.org/resource/Courteney_Cox')
        with self.assertRaises(StopIteration):
            next(self.source)

    def test_non_existing_endpoint(self) -> None:
        """
        Test if we raise a FileNotFoundError exception when the endpoint does
        not exist
        """
        with self.assertRaises(FileNotFoundError):
            self.source = SPARQLLogicalSource('$.actor.value',
                                              'http://dbpedia.org/empty',
                                              SPARQL_QUERY)

    def test_invalid_jsonpath(self) -> None:
        """
        Test if we raise a ValueError when the JSONPath expression is invalid
        """
        with self.assertRaises(ValueError):
            self.source = SPARQLLogicalSource('&$"£*W$',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)

    def test_empty_iterator(self) -> None:
        """
        Test if we handle an empty iterator
        """
        with self.assertRaises(StopIteration):
            self.source = SPARQLLogicalSource('$.actor.value',
                                              'http://dbpedia.org/sparql',
                                              SPARQL_QUERY)
            next(self.source)

if __name__ == '__main__':
    unittest.main()
