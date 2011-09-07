from parser import IncParser as Parser

class FormatParser():
    name = 'inc'
    desc = "INC reader/writer"
    extensions = ['inc']
    encoding = 'utf_8' # allowed encoding
    fallback = None

    @classmethod
    def dump_structure (cls, l10nobject):
        text = Serializer.serialize(l10nobject)
        return text

    @classmethod
    def dump_entitylist (cls, elist):
        text = Serializer.dump_entitylist(elist)
        return text

    @classmethod
    def get_entitylist (cls, text):
        l10nobject = Parser.parse_to_entitylist(text)
        return l10nobject

    @classmethod
    def get_structure (cls, text):
        l10nobject = Parser.parse(text)
        return l10nobject


def register(Manager):
    Manager.register(FormatParser)
