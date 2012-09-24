from silme.core.entity import Entity

class EntityDiff(dict):

    def __init__(self, id=None):
        self.id = id
        self.params = {}

    def add(self, type, hunk):
        """
        adds a hunk to EntityDiff.
        predefines types are: id, value
        
        hunk should be a tuple (oldval,newval) or an object that
        represents the diff
        """
        self[type] = hunk

    def hunk(self, type):
        return self[type]

    def remove_hunk(self, type):
        del self[type]

    def empty(self):
        return not bool(self)

    def add_value(self, value_old, value_new, code='default'):
        try:
            self['value'][code] = (value_old, value_new)
        except:
            self['value'] = {code: (value_old, value_new)}

    def value(self, code='default'):
        return self['value'][code]

def entity_diff (self, entity=None, code=None, struct=False):
    entitydiff = EntityDiff()
    entitydiff.id = self.id
    if code is None:
        code = self.default_code
    value1 = self.get_value(fallback=code)
    value2 = entity.get_value(fallback=code)
    if value1 != value2:
        entitydiff.add_value(value1, value2, code)
    if struct == True and self.params.has_key('source') and self.params['source']['type'] == entity.params['source']['type']:
        struct1 = self.params['source']['string'][0:self.params['source']['valpos']]+self.params['source']['string'][self.params['source']['valpos']+len(value1):]
        struct2 = entity.params['source']['string'][0:entity.params['source']['valpos']]+entity.params['source']['string'][entity.params['source']['valpos']+len(value2):]
        if struct1 != struct2:
            entitydiff.add('struct', ((struct1, self.params['source']['valpos']), (struct2, entity.params['source']['valpos'])))
    return entitydiff

Entity.diff = entity_diff

def entity_apply_diff(self, entitydiff):
    if entitydiff.has_key('value'):
        for key, value in entitydiff['value'].items():
            if self.value.has_key(key):
                self.value[key] = value[1]
    if entitydiff.has_key('struct'):
        struct = entitydiff.hunk('struct')[1]
        valpos = struct[1]
        self.params['source']['string'] = struct[0][0:valpos]+self.value+struct[0][valpos:]

Entity.apply_diff = entity_apply_diff
