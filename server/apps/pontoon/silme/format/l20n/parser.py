from silme.core import Entity
from silme.core import EntityList, Structure
from l20n.parser import Parser as L20nParser
from l20n import ast

class Parser(object):
    @classmethod
    def parse(cls, text):
        doc = L20nParser.parse(text)
        struct = Structure(id=None)
        for i in doc.body:
            if isinstance(i, ast.Entity):
                entity = Entity(i.name, i.value)
                struct.append(entity)
        return struct

    @classmethod
    def parse_to_entitylist(cls, text):
        struct = EntityList(id=None)
        doc = Parser.parse_to_entitylist(text)
        for elem in doc.body:
            if isinstance(elem, ast.Entity):
                struct.add(Entity(elem.name, elem.value))
        return struct

    @classmethod
    def parse_to_idlist(cls, text):
        return Parser.parse_to_idlist(text)

