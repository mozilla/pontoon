from .parser import DTDParser as Parser
from .structure import DTDStructure as Structure
from .serializer import DTDSerializer as Serializer

class DTDFormatParser():
    name = 'dtd'
    desc = 'DTD reader/writer'
    extensions = ['dtd']
    encoding = 'utf_8' # allowed encoding
    fallback = ['utf_8_sig']
    
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
    Manager.register(DTDFormatParser)