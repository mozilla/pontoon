from ..core import EntityList
from silme.core.types import OrderedDict, ComplexDict
from silme.core.list import EntityList, is_entitylist

def intersect(a, b):
    """ returns what's in both a and b """
    return [item for item in a if item in b] 

def difference(a, b):
    """ returns what's in b and not in a """
    return [item for item in b if not item in a] 

class EntityListDiff(ComplexDict):
    count = 0
    uri = None

    def __init__(self, id):
        self.id = id
        super(EntityListDiff, self).__init__(self)

    def empty(self):
        return not bool(len(self))

    # pos - may be a number or a tuple ('after','id') or ('before','id')
    def add(self, flag, ediff, id, pos=None):
        self[id] = {'elem': ediff, 'flags': [flag], 'pos':pos}

    def remove(self, id):
        if id in self:
            del self[id]

    def entity(self, id):
        try:
            return self[id]['elem']
        except KeyError:
            raise KeyError('No such id: %s' % id)

    def has_entity(self, id):
        return self.has_key(id)

    def entities(self, type='all'):
        entities = {}
        for id,item in self.items():
            if type=='all' or type in item['flags']:
                entities[item['elem'].id] = item['elem']
        return entities

def entitylist_diff(self, elists, flags=None, values=True):
    elists = [elists,]
    if flags == None:
        flags = ['added','removed','modified']
    elistdiff = EntityListDiff(self.id)
    elistdiff.uri = (self.uri,)+tuple(i.uri for i in elists)
    entities1 = self.keys()
    elistdiff.count = len(elists)+1
    for id in entities1:
        other = []
        for elist in elists:
            if id in elist:
                other.append(elist[id])
        entitydiff = self[id].diff(other)
        if 'value' in entitydiff and values is True:
            elistdiff.add('modified', entitydiff, id)
    return elistdiff 

def entitylist_diff2 (self, entitylist, flags=None, values=True):
    if flags == None:
        flags = ['added','removed','modified']
    entitylistdiff = EntityListDiff(self.id, ordered=self.ordered)
    entitylistdiff.uri = (self.uri, entitylist.uri)
    if not is_entitylist(entitylist):
        entitylist = entitylist.entitylist()
    entities1 = self.keys()
    entities2 = entitylist.keys()

    isect = intersect(entities1, entities2)
    if 'removed' in flags:
        for item in difference(isect, entities1):
            entitylistdiff.add('removed', ediff=self[item], id=item)
    if 'added' in flags:
        for item in difference(isect, entities2):
            if isinstance(entitylist, OrderedDict): # if we keep order
                if entitylist.keys().index(item)>0:
                    pos = ('after', entitylist.keys()[entitylist.keys().index(item)-1])
                else:
                    pos = 0
            else:
                pos = None
            entitylistdiff.add('added', ediff=entitylist[item], id=item, pos=pos)

    if ('modified' in flags and values is True) or ('unmodified' in flags):
        for item in isect:
            if values is False:
                entitylistdiff.add('unmodified', ediff=self[item], id=item)
            else:
                entity = self[item]
                entity2 = entitylist[item]
                entitydiff = entity.diff(entity2)
                if len(entitydiff.keys()) == 0:
                    if 'unmodified' in flags:
                        entitylistdiff.add('unmodified', ediff=entity, id=item)
                else:
                    if 'modified' in flags:
                        entitylistdiff.add('modified', ediff=entitydiff, id=item)
    return entitylistdiff

EntityList.diff = entitylist_diff2

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
