from ...core import Comment
from silme.core.entity import is_entity
from .parser import DTDParser as Parser


class DTDSerializer:
    @classmethod
    def serialize(cls, l10nobject):
        string = "".join([cls.dump_element(element) for element in l10nobject])
        return string

    @classmethod
    def dump_element(cls, element, fallback=None):
        if is_entity(element):
            return cls.dump_entity(element, fallback=fallback)
        elif isinstance(element, Comment):
            return cls.dump_comment(element)
        else:
            return element

    @classmethod
    def dump_entity(cls, entity, fallback=None):
        if "source" in entity.params and entity.params["source"]["type"] == "dtd":
            match = Parser.patterns["entity"].match(entity.params["source"]["string"])

            middle = entity.params["source"]["string"][
                match.end(1) : match.start(2) + 1
            ]
            end = entity.params["source"]["string"][match.end(2) - 1 :]

            if middle.endswith('"') and '"' in entity.value:
                middle = middle.replace('"', "'")
                end = end.replace('"', "'")
            elif middle.endswith("'") and "'" in entity.value:
                middle = middle.replace("'", '"')
                end = end.replace("'", '"')

            string = entity.params["source"]["string"][0 : match.start(1)]
            string += entity.id
            string += middle
            string += entity.value
            string += end
        else:
            string = "<!ENTITY " + entity.id + ' "' + entity.value + '">'
        return string

    @classmethod
    def dump_entitylist(cls, elist):
        string = "".join([cls.dump_entity(entity) + "\n" for entity in elist.values()])
        return string

    @classmethod
    def dump_comment(cls, comment):
        string = "<!--"
        for element in comment:
            string += cls.dump_element(element)
        string += "-->"
        return string
