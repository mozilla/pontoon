import silme.core
from structure import Entity as L20nEntity,Comment as L20nComment
from parser import L20nParser as Parser

import re

class L20nSerializer():
    @classmethod
    def serialize(cls, l10nobject, fallback=None):
        if not fallback:
            fallback = l10nobject.fallback
        string = u''.join([cls.dump_element(element, fallback) for element in l10nobject])
        return string

    @classmethod
    def dump_element(cls, element, fallback=None):
        if isinstance(element, silme.core.Entity) or \
           isinstance(element, L20nEntity):
            return cls.dump_entity(element, fallback=fallback)
        elif isinstance(element, silme.core.Comment) or\
             isinstance(element, L20nComment):
            return cls.dump_comment(element)
        else:
            return unicode(element)

    @classmethod
    def dump_entity(cls, entity, fallback=None):
        if isinstance(entity, L20nEntity):
            string = u'<'+entity.id+u': "'+unicode(entity.get_value(fallback))+u'"'
            if entity.kvplist:
                string += u'\n '
                string += u'\n '.join([cls.dump_kvp(kvp) for kvp in entity.kvplist])
            string += u'>'
        else:
            string = u'<'+entity.id+u': "'+unicode(entity.get_value(fallback))+u'">'
        return string

    @classmethod
    def dump_kvp(cls, kvp):
        if isinstance(kvp.value, list):
            return u'%s: [%s]' % (kvp.key, u','.join(["\"%s\"" % v for v in kvp.value]))
        else:
            return u'%s: "%s"' % (kvp.key, unicode(kvp.value))

    @classmethod
    def dump_entitylist(cls, elist, fallback=None):
        if not fallback:
            fallback = elist.fallback
        string = u''.join([cls.dump_entity(entity, fallback)+'\n' for entity in elist.get_entities()])
        return string

    @classmethod
    def dump_comment(cls, comment):
        string = u''
        if isinstance(comment, L20nComment):
          string = comment.content
        else:
            for element in comment:
                string += cls.dump_element(element)
        if string.find('\n')!=-1:
            string = re.sub('(?ms)^\s*(.*)\s*$','/* \n\\1\n */', string)
        else:
            string = re.sub('^\s*(.*)\s*$','/* \\1 */', string)
        string = re.sub('\n(?! \*)', '\n * ', string)
        return string
