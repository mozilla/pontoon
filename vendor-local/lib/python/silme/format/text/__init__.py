from serializer import TextSerializer as Serializer

class TextFormatParser():
    name = 'text'
    desc = 'Text writer'
    extensions = ['text']
    encoding = 'utf_8' # allowed encoding
    fallback = None
    
    @classmethod
    def dump_structure (cls, structure):
        text = Serializer.serialize(structure)
        return text

    @classmethod
    def dump_package (cls, l10npack):
        text = Serializer.serialize(l10npack)
        return text


    @classmethod
    def dump_entitylistdiff (cls, entitylistdiff):
        text = Serializer.dump_entitylistdiff(entitylistdiff)
        return text

    @classmethod
    def dump_structurediff (cls, structurediff):
        text = Serializer.dump_structurediff(structurediff)
        return text

    @classmethod
    def dump_packagediff (cls, packagediff):
        text = Serializer.dump_packagediff(packagediff)
        return text

    @classmethod
    def dump_entitylist (cls, entitylist):
        text = Serializer.serialize(entitylist)
        return text

def register(Manager):
    Manager.register(TextFormatParser)