from silme.core.entity import Entity, is_entity

class EntityDiff(dict):
    """
    EntityDiff is a dictionary that
    represents a difference between two Entity objects.
    It is made of hunks that applied onto one entity should
    result in a second entity, and applied onto a second
    entity with reverse option should give the first.
    """

    def __init__(self, id):
        self.id = id
        self.params = {}

    def empty(self):
        return not len(self)

    def value(self):
        return self['value']

"""
 a list of parameters of an entity to be compared.

 value[0] is a getter, value[1] is a setter - if not
 defined, key is used.
"""
test_params = {
   'id' : (),
   'value': ('values', 'value')
}

def entity_diff (self, entities):
    ediff = EntityDiff(self.id)
    if is_entity(entities):
        entities = (self, entities)
    else:
        try:
            entities = [self,] + entities
        except TypeError:
            entities = (self,) + entities
    for key, test in test_params.items():
        last = None
        value = []
        is_value_different = False
        for entity in entities:
            getter = test[0] if len(test)>0 else key
            param = getattr(entity, getter)
            if hasattr(param, '__call__'):
                nval = param.__call__()
            else:
                nval = param
            if not is_value_different and last:
                is_value_different = last!=nval
            value.append(nval)
            last = nval
    
        if is_value_different:
            ediff[key] = tuple(value) 
    return ediff

Entity.diff = entity_diff

def entity_apply_diff(self, ediff, reverse=False,
                      source=0, result=1, ignore_mismatch=False):
    if reverse:
        source, result = (result, source)
    for key, hunk in ediff.items():
        test = test_params[key]
        getter = test[0] if len(test)>0 else key
        curval = getattr(self, getter)
        if ignore_mismatch is False and curval!=hunk[source]:
            raise Exception('Hunk "%s" mismatch' % key)
        setter = test[1] if len(test)>1 else key
        setattr(self, setter, hunk[result])

Entity.apply_diff = entity_apply_diff
