from ...core import EntityList, Entity, Comment
from .structure import Structure, Section
from silme.core.list import EntityList
import re

class Parser():
    patterns = {}
    patterns['entity'] = re.compile('^\s*(\S+)\s*=\s*((?:[\S ]+(?:\n(?=\s))?)+)',re.S|re.M)
    patterns['comment'] = re.compile('^([;#][^\n]*\n?)+',re.M|re.S)
    patterns['section'] = re.compile('^\[([a-z]+)\]', re.S|re.M)


    @classmethod
    def parse(cls, text):
        struct = Structure(id=None)
        cls.build_element_list(text, struct)
        return struct

    # problem with commented out entities
    @classmethod
    def parse_to_entitylist(cls, text):
        entitylist = EntityList(id=None)
        text = cls.patterns['comment'].sub('', text)
        matchlist = cls.patterns['entity'].findall(text)
        for match in matchlist:
            entitylist.add(Entity(match[0], match[1]))
        return entitylist
    
    @classmethod
    def parse_entity(cls, text):
        match = self.patterns['entity'].match(text)
        if not match:
            raise Exception()
        entity = Entity(match.group(1))
        entity.set_value(match.group(2))
        return entity

    @classmethod
    def build_element_list (cls, text, object):
        cls.split_sections(text, object)

    @classmethod
    def split_sections(cls, text, struct, pointer=0, end=None):
        root = struct
        pattern = cls.patterns['section']
        if end:
            match = pattern.search(text, pointer, end)
        else:
            match = pattern.search(text, pointer)
        while match:
            st0 = match.start(0)
            if st0 > pointer:
                cls.split_comments(text, struct, pointer=pointer, end=st0)
                pass
            struct = Section(match.group(1))
            root.append(struct)
            pointer = match.end(0)
            if end:
                match = pattern.search(text, pointer, end)
            else:
                match = pattern.search(text, pointer)
        if (not end or (end > pointer)) and len(text) > pointer:
            cls.split_comments(text, struct, pointer=pointer, end=end)

    

    @classmethod
    def split_comments(cls, text, object, pointer=0, end=None):
        pattern = cls.patterns['comment']
        if end:
            match = pattern.search(text, pointer, end)
        else:
            match = pattern.search(text, pointer)
        while match:
            st0 = match.start(0)
            if st0 > pointer:
                cls.split_entities(text, object, pointer=pointer, end=st0)
            comment = Comment()
            cls.split_entities(match.group(0)[1:].replace('\n;','\n'), comment)
            object.append(comment)
            pointer = match.end(0)
            if end:
                match = pattern.search(text, pointer, end)
            else:
                match = pattern.search(text, pointer)
        if (not end or (end > pointer)) and len(text) > pointer:
            cls.split_entities(text, object, pointer=pointer, end=end)

    @classmethod
    def split_entities(cls, text, object, pointer=0, end=None):
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
            entity.set_value(groups[1])
            entity.params['source'] = {'type':'ini',
                                        'string':match.group(0),
                                        'valpos':match.start(2)-st0}
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
