import rdflib


class MappingReader(object):
    def __init__(self):
        self.g = rdflib.Graph()

    def read(self, path):
        format = rdflib.util.guess_format(path)
        if format != 'turtle':
            raise IOError("[R2]RML only support Turtle-format!")
        return self.g.parse(path, format=format)
