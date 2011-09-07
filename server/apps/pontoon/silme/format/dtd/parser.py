from silme.core import Entity
from silme.core import EntityList, Structure

class Parser(object):
    @classmethod
    def parse(cls, text):
        doc = dtd.Parser.parse(text)
        struct = Structure(id=None)
        for i in doc.body:
            if isinstance(i, dtd.ast.Entity):
                struct.append(Entity(i.name, i.value))
        return struct

    @classmethod
    def parse_to_entitylist(cls, text):
        struct = EntityList(id=None)
        doc = dtd.Parser.parse_to_entitylist(text)
        for elem in doc.body:
            if isinstance(elem, dtd.ast.Entity):
                struct.add(Entity(elem.name, elem.value))
        return struct

    @classmethod
    def parse_to_idlist(cls, text):
        return dtd.Parser.parse_to_idlist(text)
