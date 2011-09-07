from ...core import Comment
from .structure import Section
from .parser import Parser
from silme.core.entity import is_entity
import re

class Serializer():
    @classmethod
    def serialize(cls, l10nobject):
        string = ''.join([cls.dump_element(element) for element in l10nobject])
        return string

    @classmethod
    def dump_element(cls, element):
        if is_entity(element):
            return cls.dump_entity(element)
        elif isinstance(element, Comment):
            return cls.dump_comment(element)
        elif isinstance(element, Section):
            return cls.dump_section(element)
        else:
            return element

    @classmethod
    def dump_entity(cls, entity):
        if entity.params.has_key('source') and entity.params['source']['type']=='ini':
            match = Parser.patterns['entity'].match(entity.params['source']['string'])
            string = entity.params['source']['string'][0:match.start(1)]
            string += entity.id
            string += entity.params['source']['string'][match.end(1):match.start(2)]
            string += entity.value
            string += entity.params['source']['string'][match.end(2):]
        else:
            string = entity.id+'='+entity.value
        return string

    @classmethod
    def dump_entitylist(cls, elist):
        string = ''.join([cls.dump_entity(entity)+'\n' for entity in elist.values()])
        return string

    @classmethod
    def dump_comment(cls, comment):
        string = ''
        for element in comment:
            string += cls.dump_element(element)
        if string:
            pattern = re.compile('\n')
            string = pattern.sub('\n#', string)
            string = '#' + string
            if string.endswith('#'):
                string = string[:-1]
        return string

    @classmethod
    def dump_section(cls, section):
        string = '[%s]%s' % (section.id, cls.serialize(section))
        return string
