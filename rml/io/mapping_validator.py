from pyshacl import validate
from rdflib import Graph
from shutil import get_terminal_size


class MappingValidator:
    def __init__(self, shape: str) -> None:
        g = Graph()
        g.parse(shape, format='turtle')
        self._shape = g

    def validate(self, rules: Graph, print_report: bool = True) -> None:
        valid: bool
        report_graph: Graph
        report_text: str
        valid, report_graph, report_text = validate(rules,
                                                    shacl_graph=self._shape)
        # FIXME: Python logging module, see Gitlab issue #21
        print(f'DEBUG: RML rules valid: {valid}')
        print(f'DEBUG: SHACL validation report: {report_text}')

        # If mapping rules are invalid, print SHACL report and raise exception
        if not valid and print_report:
            self._print_report(report_text)
            raise ValueError('RML mapping rules are invalid, a detailed '
                             'explanation is available in the report')

    def _print_report(self, report_text: str) -> None:
        tty_columns: int
        tty_columns, _ = get_terminal_size()
        print('-' * tty_columns)
        title: str = 'RML rules validation report'
        white_space: int = int((tty_columns - len(title)) / 2)
        title = ' ' * white_space + title + ' ' * white_space
        print(title)
        print('-' * tty_columns)
        print(report_text)
        print('-' * tty_columns)
