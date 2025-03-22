from ...core import Entity, Comment
from .parser import IncParser as Parser
import re


class IncSerializer:
    @classmethod
    def serialize(cls, l10nobject):
        string = "".join([cls.dump_element(element) for element in l10nobject])
        return string

    @classmethod
    def dump_element(cls, element, fallback=None):
        if isinstance(element, Entity):
            return cls.dump_entity(element, fallback=fallback)
        elif isinstance(element, Comment):
            return cls.dump_comment(element)
        else:
            return element

    @classmethod
    def dump_entity(cls, entity, fallback=None):
        if (
            "source" in entity.params
            and entity.params["source"]["type"] == "properties"
        ):
            match = Parser.patterns["entity"].match(entity.params["source"]["string"])
            string = entity.params["source"]["string"][0 : match.start(1)]
            string += entity.id
            string += entity.params["source"]["string"][match.end(1) : match.start(2)]
            string += entity.get_value(fallback)
            string += entity.params["source"]["string"][match.end(2) :]
        else:
            string = "#define {} {}".format(entity.id, entity.get_value(fallback))
        return string

    @classmethod
    def dump_entitylist(cls, elist, fallback=None):
        if not fallback:
            fallback = elist.fallback
        string = "".join(
            [
                cls.dump_entity(entity, fallback) + "\n"
                for entity in elist.get_entities()
            ]
        )
        return string

    @classmethod
    def dump_comment(cls, comment):
        string = ""
        for element in comment:
            string += cls.dump_element(element)
        if string:
            pattern = re.compile("\n")
            string = pattern.sub("\n# ", string)
            string = "# " + string
            if string.endswith("# "):
                string = string[:-2]
        return string
