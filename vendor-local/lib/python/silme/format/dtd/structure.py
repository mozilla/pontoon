from ...core import Entity, Structure, Comment
import re

def process_entity(entity, subs):
    for code in entity._value.keys():
        entity._value[code] = re.sub('\&([^$]+)\;',
                                     lambda m:subs[m.group(1)],
                                     entity._value[code])

def process(self):
    if not self.params.has_key('exents') or \
       not self.params['exents']:
        return
    for elem in self:
        if isinstance(elem, Entity):
            process_entity(elem, self.params['exents'])

class DTDStructure(Structure):
    def __init__(self, id=None):
        self.process_cb = process
        Structure.__init__(self)
