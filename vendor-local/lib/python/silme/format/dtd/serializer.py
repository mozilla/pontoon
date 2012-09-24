from ...core import Entity, EntityList, Comment
from .structure import DTDStructure
from .parser import DTDParser as Parser

class DTDSerializer():
    @classmethod
    def serialize(cls, l10nobject, fallback=None):
        if not fallback:
            fallback = l10nobject.fallback
        string = u''.join([cls.dump_element(element, fallback) for element in l10nobject])
        return string

    @classmethod
    def dump_element (cls, element, fallback=None):
        if isinstance(element, Entity):
            return cls.dump_entity(element, fallback=fallback)
        elif isinstance(element,Comment):
            return cls.dump_comment(element)
        else:
            return element

    @classmethod
    def dump_entity (cls, entity, fallback=None):
        if entity.params.has_key('source') and entity.params['source']['type']=='dtd':
            match = Parser.patterns['entity'].match(entity.params['source']['string'])
            string = entity.params['source']['string'][0:match.start(1)]
            string += entity.id
            string += entity.params['source']['string'][match.end(1):match.start(2)+1]
            string += entity.get_value(fallback)
            string += entity.params['source']['string'][match.end(2)-1:]
        else:
            string = u'<!ENTITY '+entity.id+u' "'+entity.get_value(fallback)+u'">'
        return string

    @classmethod
    def dump_entitylist(cls, elist, fallback=None):
        if not fallback:
            fallback = elist.fallback
        string = u''.join([cls.dump_entity(entity, fallback)+'\n' for entity in elist.values()])
        return string

    @classmethod
    def dump_comment (cls, comment):
        string = u'<!--'
        for element in comment:
            string += cls.dump_element(element)
        string += u'-->'
        return string
