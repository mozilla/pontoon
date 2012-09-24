from ...core import EntityList, Entity, Comment
from .parser import GettextParser as Parser

import re

class GettextSerializer:
    @classmethod
    def serialize(cls, l10nobject, fallback=None):
        if not fallback:
            fallback = l10nobject.fallback
        string = ''.join([cls.dump_element(element, fallback) for element in l10nobject])
        return string

    @classmethod
    def dump_element(cls, element, fallback=None):
        if isinstance(element, Entity):
            return cls.dump_entity(element, fallback=fallback)
        elif isinstance(element,Comment):
            return cls.dump_comment(element)
        else:
            return element

    @classmethod
    def dump_entity(cls, entity, fallback=None):
        if entity.params.has_key('source') and entity.params['source']['type']=='gettext':
            match = Parser.patterns['entity'].match(entity.params['source']['string'])
            string = entity.params['source']['string'][0:match.start(1)]
            string += entity.id
            string += entity.params['source']['string'][match.end(1):match.start(2)]
            string += cls.dump_entityvalue(entity.get_value(fallback))
            string += entity.params['source']['string'][match.end(2):]
        else:
            string = 'msgid "'+entity.id+'"\nmsgstr "'+entity.get_value(fallback)+'"\n'
        return string

    @classmethod
    def dump_entityvalue(cls, value):
        v = ''
        if value.find('\n') == -1:
            return '"%s"' % value
        for line in value.split('\n'):
            v += '"%s"\n' % line
        return v[:-1] # we don't want to take the last \n added by the loop 

    @classmethod
    def dump_entitylist(cls, elist, fallback=None):
        if not fallback:
            fallback = elist.fallback
        string = ''.join([cls.dump_entity(entity, fallback)+'\n' for entity in elist.get_entities()])
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
        return string
