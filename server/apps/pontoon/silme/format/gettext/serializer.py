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
    def dump_entity(cls, entity):
        if entity.params.has_key('source') and entity.params['source']['type']=='gettext':
            match = Parser.patterns['entity'].match(entity.params['source']['string'])
            string = entity.params['source']['string'][0:match.start(1)]
            string += entity.id
            string += entity.params['source']['string'][match.end(1):match.start(2)]
            string += cls.dump_multiline_to_gettext(entity.value)
            string += entity.params['source']['string'][match.end(2):]
        else:
            id = cls.dump_multiline_to_gettext(entity.id)
            value = cls.dump_multiline_to_gettext(entity.value)
            string = 'msgid %s\nmsgstr %s\n' % (id, value)
        return string

    @classmethod
    def dump_multiline_to_gettext(cls, value):
        v = ''
        if value.find('\n') == -1:
            return '"%s"' % value
        lines = value.split('\n')
        i = 0
        for line in lines:
            if i<=len(lines)-2:
                v += '"%s\\n"\n' % line
            else:
                v += '"%s"' % line
            i+=1
        return v 

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
        return string
