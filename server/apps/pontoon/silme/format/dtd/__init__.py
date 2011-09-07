from .parser import Parser
from .serializer import Serializer

class FormatParser():
    name = 'dtd'
    desc = 'DTD reader/writer'
    extensions = ['dtd']
    encoding = 'utf_8' # allowed encoding
    fallback = ['utf_8_sig']
    
    @classmethod
    def dump_structure(cls, l10nobject):
        text = Serializer.serialize(l10nobject)
        return text

    @classmethod
    def dump_entitylist(cls, elist):
        text = Serializer.serialize_entitylist(elist)
        return text

    @classmethod
    def get_idlist(cls, text):
        return Parser.parse_to_idlist(text)

    @classmethod
    def get_entitylist(cls, text):
        return Parser.parse_to_entitylist(text)

    @classmethod
    def get_structure(cls, text):
        return Parser.parse(text)

def register(Manager):
    Manager.register(FormatParser)
