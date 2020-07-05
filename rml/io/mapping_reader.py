from rdflib import Graph

class MappingReader(object):
    def __init__(self) -> None:
        self._graph: Graph = Graph()

    def read(self, path: str) -> Graph:
        try:
            rules = self._graph.parse(path, format='turtle')
        except FileNotFoundError:
            raise FileNotFoundError(f'Unable to open {path}')
        except Exception:
            raise ValueError(f'Unable to parse {path} as Turtle')
        return rules
