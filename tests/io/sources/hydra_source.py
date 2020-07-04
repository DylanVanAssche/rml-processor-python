#!/usr/bin/env python

import unittest
from json.decoder import JSONDecodeError
from lxml.etree import XMLSyntaxError, XPathEvalError
from rdflib.term import Literal, URIRef

from rml.io.sources import HydraLogicalSource, MIMEType

QUERY="""
PREFIX lc:  <http://semweb.mmlab.be/ns/linkedconnections#>
SELECT ?connection ?departure ?arrival
WHERE {
    ?connection lc:departureStop ?departure .
    ?connection lc:arrivalStop ?arrival .
}
ORDER BY DESC(?connection)
"""

class HydraLogicalSourceTests(unittest.TestCase):

    def test_non_existing_resource(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the resource
        does not exist
        """
        with self.assertRaises(FileNotFoundError):
            source = HydraLogicalSource('http://graph.irail.be/empty',
                                             MIMEType.JSON_LD)

    def test_non_existing_url(self) -> None:
        """
        Test if a FileNotFoundError exception is raised when the url cannot be
        resolved
        """
        with self.assertRaises(FileNotFoundError):
            source = HydraLogicalSource('http://non-existing-url.be',
                                             MIMEType.JSON_LD)

    def test_iterator_jsonld(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.jsonld',
                                    MIMEType.JSON_LD,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_iterator_rdfxml(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.rdf',
                                    MIMEType.RDF_XML,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_iterator_turtle(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.ttl',
                                    MIMEType.TURTLE,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_iterator_ntriples(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.ntriples',
                                    MIMEType.NTRIPLES,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_iterator_nquads(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.nquads',
                                    MIMEType.NQUADS,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_iterator_trig(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.trig',
                                    MIMEType.TRIG,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_iterator_trix(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.trix',
                                    MIMEType.TRIX,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

    def test_iterator_n3(self) -> None:
        """
        Test if we can iterate over every row
        """
        source = HydraLogicalSource('http://127.0.0.1:8000/tests/assets/hydra/connections0.n3',
                                    MIMEType.N3,
                                    reference_formulation=QUERY)

        # Hydra page 0
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8883808/20200619/IC1717'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008883808'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814332'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8814159/20200619/IC2039'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008814159'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008814167'))

        # Hydra page 1
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8895430/20200619/P8903'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008895430'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008895422'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8813003/20200619/IC2118'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008813003'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008813045'))

        # Hydra page 2
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8833274/20200619/IC2640'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008833274'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008833266'))
        connection, departure, arrival = next(source)
        self.assertEqual(connection, URIRef('http://irail.be/connections/8811262/20200619/IC2240'))
        self.assertEqual(departure, URIRef('http://irail.be/stations/NMBS/008811262'))
        self.assertEqual(arrival, URIRef('http://irail.be/stations/NMBS/008811254'))

        with self.assertRaises(StopIteration):
            next(source)

if __name__ == '__main__':
    unittest.main()
