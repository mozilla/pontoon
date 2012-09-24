from ..core import EntityList, Entity

def intersect(a, b):
    """ returns what's in both a and b """
    return list(set(a) & set(b))

def difference(a, b):
    """ returns what's in b and not in a """
    return [item for item in b if not item in a] 

class EntityListDiff(dict):
    def __init__(self):
        self.id = None
        self.uri = None
        self._keys = []

    def __iter__(self):
        for i in self._keys:
            yield (i,self[i])

    def empty(self):
        return not bool(len(self))

    # pos - may be a number or a tuple ('after','id') or ('before','id')
    def add(self, flag, entity, id, pos=None):
        self[id] = {'elem': entity, 'flags': [flag], 'pos':pos}
        self._keys.append(id)

    def remove(self, id):
        if id in self:
            del self[id]
            del self._keys[id]

    def entity(self, id):
        try:
            return self[id]['elem']
        except KeyError:
            raise KeyError('No such id: '+id)

    def has_entity(self, id):
        return self.has_key(id)

    def entities(self, type='all'):
        entities = {}
        for item in self.values():
            if type=='all' or type in item['flags']:
                if isinstance(item['elem'], Entity):
                    item['elem'].params['diff_flags'] = item['flags']
                entities[item['elem'].id] = item['elem']
        return entities

def entitylist_diff (self, entitylist, flags=None, values=True):
    if flags == None:
        flags = ['added','removed','modified']
    entitylistdiff = EntityListDiff()
    entitylistdiff.id = self.id
    entitylistdiff.uri = (self.uri, entitylist.uri)
    if not isinstance(entitylist, EntityList):
        entitylist = entitylist.entitylist() 
    entities1 = self.ids()
    entities2 = entitylist.ids()

    isect = intersect(entities1, entities2)
    if 'removed' in flags:
        for item in difference(isect, entities1):
            entitylistdiff.add('removed', id=item, entity=self[item])
    if 'added' in flags:
        for item in difference(isect, entities2):
            if entitylist._keys: # if we keep order
                if entitylist._keys.index(item)>0:
                    pos = ('after', entitylist._keys[entitylist._keys.index(item)-1])
                else:
                    pos = 0
            else:
                pos = None
            entitylistdiff.add('added', id=item, entity=entitylist[item], pos=pos)

    if ('modified' in flags and values is True) or ('unmodified' in flags):
        for item in isect:
            if values is False:
                entitylistdiff.add('unmodified', id=item, entity=self[item])
            else:
                entity = self[item]
                entity2 = entitylist[item]
                entitydiff = entity.diff(entity2)
                if entitydiff.empty():
                    if 'unmodified' in flags:
                        entitylistdiff.add('unmodified', id=item, entity=entity)
                else:
                    if 'modified' in flags:
                        entitylistdiff.add('modified', id=item, entity=entitydiff)
    return entitylistdiff

EntityList.diff = entitylist_diff

def entitylist_apply_diff (self, entitylistdiff):
    for key, item in entitylistdiff.items():
        if 'removed' in item['flags']:
            self.remove_entity(key)
        elif 'modified' in item['flags']:
            self.entity(key).apply_diff(item['elem'])
        elif 'added' in item['flags']:
            if isinstance(item['elem'], tuple):
                self.add(item['elem'][0], pos=item['elem'][1])
            else:
                self.add(item['elem'])

EntityList.apply_diff = entitylist_apply_diff
