from l20n.ast import Entity
from .parser import Parser
from .serializer import Serializer
from l20n.compiler.js import Compiler as JsCompiler
from silme.core import EntityList

class FormatParser():
    name = 'l20n'
    desc = "L20n reader/writer"
    extensions = ['lol']
    encoding = 'utf_8' # allowed encoding
    fallback = None

    @classmethod
    def dump_structure(cls, struct):
        text = Serializer.serialize(struct)
        return text

    @classmethod
    def dump_entitylist(cls, elist):
        text = Serializer.dump_entitylist(elist)
        return text

    @classmethod
    def get_entitylist(cls, text):
        struct = cls.get_structure(text)
        entitylist = EntityList()
        for i in struct:
            if isinstance(i, Entity):
                entitylist.add(i)
        return entitylist

    @classmethod
    def get_structure(cls, text):
        return Parser.parse(text)
    
    @classmethod
    def compile(cls, structure, format='js'):
        if format=='js':
            c = JsCompiler()
        else:
            c = PyCompiler()
        j20n = c.compile(structure)
        return j20n

def register(Manager):
    Manager.register(FormatParser)
