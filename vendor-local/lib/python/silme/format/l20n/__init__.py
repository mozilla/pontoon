from .parser import L20nParser as Parser
from .structure import LOL as Structure
from .serializer import L20nSerializer as Serializer

class L20nFormatParser ():
    name = 'l20n'
    desc = "L20n reader/writer"
    extensions = ['lol']
    encoding = 'utf_8' # allowed encoding
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
        l10nobject = cls.get_l10nobject(text, code=code)
        entitylist = EntityList()
        for i in l10nobject.structure:
            if isinstance(i, Entity):
                entitylist.add_entity(silme.core.entity.Entity(i.id, i.get_value()))
        return entitylist

    @classmethod
    def get_structure (cls, text, code='default'):
        l10nobject = Parser().parse(text)
        return l10nobject

def register(Manager):
    Manager.register(L20nFormatParser)
