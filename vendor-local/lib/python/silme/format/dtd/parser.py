from ...core import Entity, EntityList, Comment
from .structure import DTDStructure
import re

class DTDParser():
    name_start_char = u':A-Z_a-z\xC0-\xD6\xD8-\xF6\xF8-\u02FF' + \
            u'\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF'+\
            u'\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD'
    name_char = name_start_char + ur'\-\.0-9' + u'\xB7\u0300-\u036F\u203F-\u2040'
    name = u'[' + name_start_char + u'][' + name_char + u']*'

    patterns = {}
    patterns['entity'] = re.compile(u'<!ENTITY\s+(' + name + u')\s+((?:\"[^\"]*\")|(?:\'[^\']*\'))\s*>', re.S|re.U)
    patterns['comment'] = re.compile(u'\<!\s*--(.*?)(?:--\s*\>)', re.M|re.S)

    @classmethod
    def parse(cls, text, code='default'):
        dtd = DTDStructure()
        cls.build_element_list(text, dtd, code=code)
        dtd.fallback = code
        return dtd

    @classmethod
    def parse_to_entitylist(cls, text, code='default'):
        entitylist = EntityList()
        text = cls.patterns['comment'].sub('', text)
        matchlist = cls.patterns['entity'].findall(text)
        for match in matchlist:
            entitylist.add_entity(Entity(match[0], match[1][1:-1], code))
        return entitylist

    @classmethod
    def parse_entity(cls, text, code='default'):
        match = self.patterns['entity'].match(text)
        if not match:
            raise Exception()
        entity = Entity(match.group(0))
        entity.set_value(match.group(1)[1:-1], code)
        return entity


    @classmethod
    def build_element_list (cls, text, object, type='comment', code='default', pointer=0, end=None):
        cls.split_comments(text, object, code)

    @classmethod
    def split_comments (cls, text, object, code='default', pointer=0, end=None):
        pattern = cls.patterns['comment']
        if end:
            match = pattern.search(text, pointer, end)
        else:
            match = pattern.search(text, pointer)
        while match:
            st0 = match.start(0)
            if st0 > pointer:
                cls.split_entities(text, object, code=code, pointer=pointer, end=st0)
            comment = Comment()
            cls.split_entities(match.group(1), comment, code=code)
            object.append(comment)
            pointer = match.end(0)
            if end:
                match = pattern.search(text, pointer, end)
            else:
                match = pattern.search(text, pointer)
        if len(text) > pointer:
            cls.split_entities(text, object, code=code, pointer=pointer)

    @classmethod
    def split_entities (cls, text, object, code='default', pointer=0, end=None):
        pattern = cls.patterns['entity']
        if end:
            match = pattern.search(text, pointer, end)
        else:
            match = pattern.search(text, pointer)
        while match:
            st0 = match.start(0)
            if st0 > pointer:
                object.append(text[pointer:st0])
            groups = match.groups()
            entity = Entity(groups[0])
            entity.set_value(groups[1][1:-1], code)
            entity.params['source'] = {'type':'dtd',
                                        'string':match.group(0),
                                        'valpos':match.start(2)+1-st0}
            object.append(entity)
            pointer = match.end(0)
            if end:
                match = pattern.search(text, pointer, end)
            else:
                match = pattern.search(text, pointer)
        if (not end or (end > pointer)) and len(text) > pointer:
            if end:
                object.append(text[pointer:end])
            else:
                object.append(text[pointer:])
