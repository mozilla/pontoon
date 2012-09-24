from .parser import GettextParser as Parser
from .structure import GettextStructure as Structure
from .serializer import GettextSerializer as Serializer

class GettextFormatParser():
    name = 'gettext'
    desc = "GetText format parser"
    extensions = ['po']
    encoding = 'utf8' # allowed encoding
    fallback = None

    @classmethod
    def dump_structure (cls, l10nobject):
        text = Serializer.serialize(l10nobject)
        return text

    @classmethod
    def dump_entitylist (cls, elist):
        text = Serializer.dump_entitylist(elist)
        return text

    @classmethod
    def get_entitylist (cls, text, code='default'):
        l10nobject = Parser.parse_to_entitylist(text, code=code)
        return l10nobject

    @classmethod
    def get_structure (cls, text, code='default'):
        l10nobject = Parser.parse(text, code=code)
        return l10nobject

def register(Manager):
    Manager.register(GettextFormatParser)
