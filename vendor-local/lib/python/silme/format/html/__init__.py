from .parser import HTMLParser as Parser
from .structure import HTMLStructure as Structure
from .serializer import HTMLSerializer as Serializer

class HTMLFormatParser():
    name = 'html'
    desc = "HTML L10n format parser"
    extensions = ['html']
    encoding = None # allowed encoding
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

    @classmethod
    def dump_entitylistdiff (cls, entitylistdiff):
        text = Serializer.dump_entitylistdiff(entitylistdiff)
        return text

    @classmethod
    def dump_structurediff (cls, structurediff):
        text = Serializer.dump_l10nobjectdiff(structurediff)
        return text

    @classmethod
    def dump_packagediff (cls, packagediff):
        text = Serializer.dump_packagediff(packagediff)
        return text

def register(Manager):
    Manager.register(HTMLFormatParser)
