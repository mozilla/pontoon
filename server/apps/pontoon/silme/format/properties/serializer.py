from ...core import EntityList, Entity, Comment
from silme.core.entity import is_entity
from .structure import PropertiesStructure
from .parser import PropertiesParser as Parser
import re

class PropertiesSerializer():
    @classmethod
    def serialize(cls, l10nobject):
        string = u''.join([cls.dump_element(element) for element in l10nobject])
        return string

    @classmethod
    def dump_element(cls, element, fallback=None):
        if is_entity(element):
            return cls.dump_entity(element)
        elif isinstance(element,Comment):
            return cls.dump_comment(element)
        else:
            return element

    @classmethod
    def dump_entity (cls, entity):
        if entity.params.has_key('source') and entity.params['source']['type']=='properties':
            match = Parser.patterns['entity'].match(entity.params['source']['string'])
            string = entity.params['source']['string'][0:match.start(1)]
            string += entity.id
            string += entity.params['source']['string'][match.end(1):match.start(2)]
            string += entity.value
            string += entity.params['source']['string'][match.end(2):]
        else:
            string = entity.id+u' = '+entity.value
        return string

    @classmethod
    def dump_entitylist(cls, elist):
        string = u''.join([cls.dump_entity(entity)+'\n' for entity in elist.values()])
        return string

    @classmethod
    def dump_comment (cls, comment):
        string = u''
        for element in comment:
            string += cls.dump_element(element)
        if string:
            pattern = re.compile('\n')
            string = pattern.sub('\n#', string)
            string = '#' + string
            if string.endswith('#'):
                string = string[:-1]
        return string
