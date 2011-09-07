

class Serializer():
    @classmethod
    def serialize(cls, struct):
        entities = [dtd.ast.Entity(entity.id, entity.value) for entity in struct.entities()]
        doc = dtd.ast.DTD(entities)
        return dtd.Serializer.serialize(doc)

    @classmethod
    def serialize_entitylist(cls, elist):
        entities = [dtd.ast.Entity(entity.id, entity.value) for entity in elist.values()]
        doc = dtd.ast.DTD(entities)
        return dtd.Serializer.serialize(doc)

