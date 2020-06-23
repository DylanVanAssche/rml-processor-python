#!/usr/bin/env python

import unittest
from rdflib.term import URIRef

from rml.sources import MIMEType
from rml.maps import SubjectMap, TermType

class SubjectMapTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def test_unknown_termtype(self) -> None:
        """
        Test if we raise a ValueError when TermType is unknown
        """
        with self.assertRaises(ValueError):
            sm = SubjectMap('http://example.com/{id}', TermType.UNKNOWN,
                            MIMEType.CSV)
            sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_empty_template(self) -> None:
        """
        Test if we can resolve an empty template using CSV data
        """
        sm = SubjectMap('http://example.com/', TermType.TEMPLATE,
                        MIMEType.CSV)
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})

    def test_non_existing_reference(self) -> None:
        """
        Test if we can resolve an non existing reference using CSV data.
        This can happen when a certain column has NULL values.
        In this test case, only the first row has a valid value, others are
        NULL. No subject may be generated when the reference does not exist.
        """
        sm = SubjectMap('title', TermType.REFERENCE,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65',
                           'title': 'King'})
        # Subject generated
        self.assertEqual(subj, URIRef('King'))

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})

        # No subject generated
        with self.assertRaises(NameError):
            subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})

    def test_csv_template(self) -> None:
        """
        Test if we can resolve a template using CSV data
        """
        sm = SubjectMap('http://example.com/{id}', TermType.TEMPLATE,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://example.com/0'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://example.com/1'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://example.com/2'))

    def test_csv_reference(self) -> None:
        """
        Test if we can resolve a reference using CSV data
        """
        sm = SubjectMap('name', TermType.REFERENCE,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('Herman'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('Ann'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('Simon'))

    def test_constant(self) -> None:
        """
        Test if we can resolve a constant using CSV data
        """
        sm = SubjectMap('http://xmlns.com/foaf/0.1/Person', TermType.CONSTANT,
                        MIMEType.CSV)
        subj = sm.resolve({'id': '0', 'name': 'Herman', 'age': '65'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '1', 'name': 'Ann', 'age': '62'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))
        subj = sm.resolve({'id': '2', 'name': 'Simon', 'age': '23'})
        self.assertEqual(subj, URIRef('http://xmlns.com/foaf/0.1/Person'))

if __name__ == '__main__':
    unittest.main()
