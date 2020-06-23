from uritemplate import URITemplate
from rdflib.term import URIRef, Identifier
from jsonpath_ng import parse

from . import TermMap, TermType
from ..sources import MIMEType

class SubjectMap(TermMap):
    def __init__(self, term: str, term_type: TermType,
                 reference_formulation: MIMEType) -> None:
        super().__init__(term, term_type, reference_formulation)

    def resolve(self, data) -> Identifier:
        if self._term_type == TermType.TEMPLATE:
            return URIRef(self._resolve_template(data))
        elif self._term_type == TermType.REFERENCE:
            return URIRef(self._resolve_reference(self._term, data))
        elif self._term_type == TermType.CONSTANT:
            return URIRef(self._term)
        else:
            raise ValueError(f'Unknown term type: {self._term_type}')

    def _resolve_template(self, data) -> str:
        # term.expand() is broken when an XPath expression is used
        # https://github.com/python-hyper/uritemplate/issues/56
        ###########################################################
        #term = URITemplate(self._term)
        #variables = term.variables
        #resolved_variables = {}

        ## Resolve each variable in template
        #if variables:
        #    for var in variables:
        #        var = str(var)
        #        resolved_var = self._resolve_reference(var, data)
        #        resolved_variables[var] = resolved_var
        #    print(resolved_variables)

        #    # Expand template
        #    # term = term.expand(var_dict=resolved_variables)
        #else:
        #    raise NameError(f'Template is empty: {self._term}')
        #return str(term)

        term = URITemplate(self._term)
        variables = term.variables
        term = str(term)

        if variables:
            for var in variables:
                var = str(var)
                resolved_var = self._resolve_reference(var, data)
                var = '{' + var + '}'
                term = term.replace(var, resolved_var)
                print(term)
        else:
            raise NameError(f'Template is empty: {self._term}')

        return term

    def _resolve_reference(self, reference, data) -> str:
        # XPath reference (XML)
        if self._reference_formulation == MIMEType.APPLICATION_XML or \
           self._reference_formulation == MIMEType.TEXT_XML:
            try:
                ref = data.xpath(reference)[0]
                ref = ref.text
                print(ref)
                return ref
            except IndexError:
                raise NameError(f'Reference {reference} invalid XPath')
        # JSONPath reference (JSON)
        elif self._reference_formulation == MIMEType.JSON:
            try:
                jsonpath = parse(reference)
                ref = jsonpath.find(data)[0]
                ref = ref.value
                print(ref)
                return ref
            except:
                raise NameError(f'Reference {reference} invalid JSONPath')
        # Key-Value reference (CSV, TSV, SQL, RDF, SPARQL, Hydra, ...)
        elif self._reference_formulation == MIMEType.CSV or \
             self._reference_formulation == MIMEType.TSV or \
             self._reference_formulation == MIMEType.SQL or \
             self._reference_formulation == MIMEType.JSON_LD or \
             self._reference_formulation == MIMEType.N3 or \
             self._reference_formulation == MIMEType.NQUADS or \
             self._reference_formulation == MIMEType.NTRIPLES or \
             self._reference_formulation == MIMEType.RDF_XML or \
             self._reference_formulation == MIMEType.TRIG or \
             self._reference_formulation == MIMEType.TRIX or \
             self._reference_formulation == MIMEType.TURTLE:
            try:
                ref = data[reference]
                print(ref)
                return ref
            except KeyError:
                raise NameError(f'Reference {reference} not found in {data}')

