from ...core import Entity, Comment
from .structure import DTDStructure
from silme.core.list import EntityList
import re


class DTDParser:
    name_start_char = (
        ":A-Z_a-z\xC0-\xD6\xD8-\xF6\xF8-\u02FF"
        "\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF"
        "\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD"
    )
    name_char = name_start_char + r"\-\.0-9" + "\xB7\u0300-\u036F\u203F-\u2040"
    name = "[" + name_start_char + "][" + name_char + "]*"

    patterns = {
        "id": re.compile(r"<!ENTITY\s+(" + name + ")[^>]*>", re.S | re.U),
        "entity": re.compile(
            r"<!ENTITY\s+(" + name + r")\s+((?:\"[^\"]*\")|(?:'[^']*'))\s*>",
            re.S | re.U,
        ),
        "comment": re.compile(r"\<!\s*--(.*?)(?:--\s*\>)", re.M | re.S),
    }

    @classmethod
    def parse(cls, text):
        dtd = DTDStructure(id=None)
        cls.build_element_list(text, dtd)
        return dtd

    @classmethod
    def parse_to_idlist(cls, text):
        text = cls.patterns["comment"].sub("", text)
        ids = [m[0] for m in cls.patterns["id"].findall(text)]
        return ids

    @classmethod
    def parse_to_entitylist(cls, text):
        elist = EntityList(id=None)
        text = cls.patterns["comment"].sub("", text)
        for match in cls.patterns["entity"].findall(text):
            elist.add(Entity(match[0], match[1][1:-1]))
        return elist

    @classmethod
    def parse_entity(cls, text):
        match = cls.patterns["entity"].match(text)
        if not match:
            raise Exception()
        entity = Entity(match.group(0))
        entity.set_value(match.group(1)[1:-1])
        return entity

    @classmethod
    def build_element_list(
        cls, text, obj, type="comment", code="default", pointer=0, end=None
    ):
        cls.split_comments(text, obj, code)

    @classmethod
    def split_comments(cls, text, obj, code="default", pointer=0, end=None):
        pattern = cls.patterns["comment"]
        if end:
            match = pattern.search(text, pointer, end)
        else:
            match = pattern.search(text, pointer)
        while match:
            st0 = match.start(0)
            if st0 > pointer:
                cls.split_entities(text, obj, code=code, pointer=pointer, end=st0)
            comment = Comment()
            cls.split_entities(match.group(1), comment, code=code)
            obj.append(comment)
            pointer = match.end(0)
            if end:
                match = pattern.search(text, pointer, end)
            else:
                match = pattern.search(text, pointer)
        if len(text) > pointer:
            cls.split_entities(text, obj, code=code, pointer=pointer)

    @classmethod
    def split_entities(cls, text, obj, code="default", pointer=0, end=None):
        pattern = cls.patterns["entity"]
        if end:
            match = pattern.search(text, pointer, end)
        else:
            match = pattern.search(text, pointer)
        while match:
            st0 = match.start(0)
            if st0 > pointer:
                obj.append(text[pointer:st0])
            groups = match.groups()
            entity = Entity(groups[0])
            entity.set_value(groups[1][1:-1])
            entity.params["source"] = {
                "type": "dtd",
                "string": match.group(0),
                "valpos": match.start(2) + 1 - st0,
            }
            obj.append(entity)
            pointer = match.end(0)
            if end:
                match = pattern.search(text, pointer, end)
            else:
                match = pattern.search(text, pointer)
        if (not end or (end > pointer)) and len(text) > pointer:
            if end:
                obj.append(text[pointer:end])
            else:
                obj.append(text[pointer:])
