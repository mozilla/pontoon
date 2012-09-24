from silme.core import EntityList, Entity, Comment
from .structure import GettextStructure
import re

class GettextParser():
    patterns = {}
    patterns['entity'] = re.compile('^msgid "([^"]*)"\nmsgstr ((?:"[^"]*"\n?)*(?:"[^"]*"))$',re.M|re.S)
    patterns['comment'] = re.compile('^#([^\n]*)$',re.M)
    patterns['msgctxt'] = re.compile('^msgctxt [^\n]*\n',re.M|re.S)

    @classmethod
    def parse(cls, text, code='default'):
        po = GettextStructure()
        cls.build_element_list(text, po, code=code)
        po.fallback = code
        return po

    @classmethod
    def parse_to_entitylist(cls, text, code='default'):
        entityList = EntityList()
        text = cls.patterns['comment'].sub('', text)
        matchlist = cls.patterns['entity'].findall(text)
        for match in matchlist:
            if match[0]:
                entityList.add_entity(Entity(match[0], match[1], code))
        return entityList

    @classmethod
    def build_element_list (cls, text, object, type='comment', code='default', pointer=0, end=None):
        cls.split_msgctxt(text, object, code)

    @classmethod
    def split_msgctxt(cls, text, object, code='default', pointer=0, end=None):
        '''
        this method removes all msgctxt for now (we don't know how to parse them anyway)
        '''
        pattern = cls.patterns['msgctxt']
        text = re.sub(pattern, '', text)
        cls.split_comments(text, object, code=code, pointer=pointer, end=end)

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
            if len(object) and isinstance(object[-1], Comment):
                object[-1].add_elements(comment)
            elif len(object)>1 and (isinstance(object[-2], Comment) and
                                    object[-1]=='\n'):
                object[-2].add_string(object[-1])
                object[-2].add_elements(comment)
                del object[-1]
            else:
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
            if match.start(0) > pointer:
                object.append(text[pointer:match.start(0)])
            entity = Entity(match.group(1), cls._clean_value(match.group(2)))
            entity.params['source'] = {'type': 'gettext',
                                        'string': match.group(0),
                                        'valpos':match.start(2)-match.start(0)}
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
        return object

    @classmethod
    def _clean_value(cls, text):
        return text.replace('"', '')
