from l20n.serializer import Serializer as L20nSerializer
from silme.core.types.odict import OrderedDict
from l20n import ast
import silme
from silme.core.entity import is_string

import re

class Serializer(object):
    @classmethod
    def serialize(cls, struct):
        lol = cls.convert_to_ast(struct)
        return L20nSerializer.serialize(lol)

    @classmethod
    def convert_to_ast(cls, struct):
        lol = ast.LOL()
        for item in struct:
            if isinstance(item, silme.core.Entity):
                id = ast.Identifier(item.id)
                if not item.value:
                    value = None
                else:
                    value = cls.convert_value(item.value)
                attrs = None
                if 'attrs' in item.params:
                    attrs = []
                    for k,v in item.params['attrs'].items():
                        attrs.append(ast.KeyValuePair(ast.Identifier(k),
                                                      cls.convert_value(v)))
                entity = ast.Entity(id=id,
                                    value=value,
                                    attrs=attrs)
                lol.body.append(entity)
        return lol

    @classmethod
    def convert_value(cls, value):
        if is_string(value):
            m = re.finditer('{{([^}]+)}}', value)
            nv = []
            pt = 0
            for match in m:
                if match.start(0) > pt:
                    nv.append(ast.String(value[pt:match.start(0)]))
                nv.append(ast.Identifier(match.group(1)))
                pt = match.end(0)
            if pt < len(value) or len(nv) == 0:
                nv.append(ast.String(value[pt:]))
            if len(nv) == 1 and isinstance(nv[0], ast.String):
                return nv[0]
            return ast.ComplexString(nv)
        elif isinstance(value, list):
            v = map(cls.convert_value, value)
            return ast.Array(v)
        elif isinstance(value, dict):
            d = OrderedDict()
            for k,v in value.items():
                d[ast.Identifier(k)] = cls.convert_value(v)
            return ast.Hash(d)
        raise Exception()
