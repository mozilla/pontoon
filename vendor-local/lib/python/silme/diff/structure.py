from ..core import Entity, Blob, Structure, Comment
from .list import EntityListDiff
from .entity import EntityDiff
from difflib import *

def compare_lists(list1, list2):
    resultlist = []
    s = SequenceMatcher(None, list1, list2)
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        resultlist.append((tag, i1, i2, j1, j2))
    return resultlist

def compare_structures (l10nobject1, l10nobject2):
    structure1 = []
    structure2 = []
    for i in l10nobject1:
        if isinstance(i, Entity):
            structure1.append(u'E'+i.id)
        elif isinstance(i, unicode):
            structure1.append(u'U')
        elif isinstance(i, Comment):
            structure1.append(u'C')
    for i in l10nobject2:
        if isinstance(i, Entity):
            structure2.append(u'E'+i.id)
        elif isinstance(i, unicode):
            structure2.append(u'U')
        elif isinstance(i, Comment):
            structure2.append(u'C')
    difftype = compare_lists(structure1, structure2)
    return difftype

class StructureDiff(list):
    def __init__(self):
        list.__init__(self)
        self.id = None
        self.uri = None

    def empty(self):
        return not bool(len(self))

    def entitylistdiff(self):
        entitylistdiff = EntityListDiff()
        entitylistdiff.id = self.id
        entitylistdiff.uri = self.uri
        entities = self.entities(type='all')
        for entity in entities.values():
            flags = entity.params['diff_flags']
            if 'modified' in flags:
                entitylistdiff.add('modified', entity=entity, id=entity.id)
            elif 'added' in flags:
                entitylistdiff.add('added', entity=entity, id=entity.id)
            elif 'removed' in flags:
                entitylistdiff.add('removed', entity=entity, id=entity.id)
        return entitylistdiff

    def has_entity(self, id):
        entities = self.get_entities(type='all')
        for entity in entities.values():
            if entity.id == id:
                flags = entity.params['diff_flags']
                return True
        return False

    def entity(self, id):
        entities = self.get_entities(type='all')
        for entity in entities.values():
            if entity.id == id:
                flags = entity.params['diff_flags']
                return {'elem': entity, 'flags': entity.params['diff_flags'], 'pos':None}
        raise KeyError('No such id: '+id)

    def entities(self, type='all'):
        (added, removed, modified) = {},{},{}

        def _get_entities_of_type(chunks, type):
            current = added if type=='added' else removed
            opposite = added if type=='removed' else removed
            for elem in chunks:
                if isinstance(elem, Entity):
                    if opposite.has_key(elem.id):
                        entitydiff = elem.diff(opposite[elem.id])
                        if not entitydiff.empty():
                            entitydiff.params['diff_flags'] = ['modified']
                            modified[elem.id] = entitydiff
                        del opposite[elem.id]
                    else:
                        elem.params['diff_flags'] = type
                        current[elem.id] = elem

        for i in self:
            if 'modified' in i['flags'] and isinstance(i['elements'][1], EntityDiff):
                if i['elements'][1].has_key('value'):
                    modified[i['elements'][0]] = i['elements'][1]
                    modified[i['elements'][0]].params['diff_flags'] = i['flags']
            elif 'added' in i['flags']:
                _get_entities_of_type(i['elements'], 'added')
            elif 'removed' in i['flags']:
                _get_entities_of_type(i['elements'], 'removed')
            elif 'replaced' in i['flags']:
                _get_entities_of_type(i['elements'], 'removed')
                _get_entities_of_type(i['elements2'], 'added')
        
        entities = {}
        if type == 'all' or 'modified' in type:
            entities.update(modified)
        if type == 'all' or 'added' in type:
            entities.update(added)
        if type == 'all' or 'removed' in type:
            entities.update(removed)
        return entities

    def add(self, type, element):
        chunk = {'flags':[type]}
        chunk['elements'] = element
        self.append(chunk)

def get_prev_elements (self, pos):
    prev_elements = []
    while len(prev_elements) < 3:
        if pos > 0:
            pos = pos-1
            prev_elements.append(self[pos])
        else:
            prev_elements.append('BEGIN')
            break
    return prev_elements

Structure.get_prev_elements = get_prev_elements

def get_next_elements (self, pos):
    next_elements = []
    while len(next_elements) < 3:
        if pos < len(self):
            next_elements.append(self[pos])
            pos = pos+1
        else:
            next_elements.append('END')
            break
    return next_elements

Structure.get_next_elements = get_next_elements


def locate_position (self, prev_elements, next_elements, chunk_size=None, by='any', mode=''):
    pos = None
    if by == 'any':
        pos = self.locate_position(prev_elements, next_elements, chunk_size=chunk_size, by='entity', mode=mode)
        if pos == None:
            pos = self.locate_position(prev_elements, next_elements, chunk_size=chunk_size, by= 'marker', mode=mode)
        return pos

    for p, elem in enumerate(prev_elements):
        if by == 'entity' and isinstance(elem, Entity):
            pos = self.locate_entity(elem)
            if pos != None:
                pos = pos+p+1
                break
        elif by == 'marker' and elem == 'BEGIN':
            pos = p
            break
    if pos == None and chunk_size != None:
        for p, elem in enumerate(next_elements):
            if by == 'entity' and isinstance(elem, Entity):
                pos = self.locate_entity(elem)
                if pos != None:
                    pos = pos-p
                    break
            elif by == 'marker' and elem == 'END':
                pos = len(self)-p
                break
        if pos != None and mode == 'added':
            pos = pos + 1 # in case we're adding following the nextElements we need to set up position +1
        if pos != None:
            pos = pos - chunkSize + 1
    return pos

Structure.locate_position = locate_position


def locate_entity (self, entity):
    pos = self.get_entity_position(entity.id)
    return pos

Structure.locate_entity = locate_entity

def locate_comment (cls, l10nobject, comment):
    pos = None
    for p, i in enumerate(l10nobject.structure):
        if isinstance(i, Comment):
            pos = p
            break
    return pos

Structure.locate_comment = locate_comment

def guess_spacing (cls, l10nobject, pos, spc_num=3, ext='dtd', entity=None):
    spacing = 1
    return spacing

Structure.guess_spacing = guess_spacing

def l10nobject_diff (self, l10nobject, flags=None, values=True):
    if flags == None:
        flags = ['added','removed','modified','replaced']
    l10nobject_diff = StructureDiff()
    if self.id is not None:
        l10nobject_diff.id = self.id
    l10nobject_diff.uri = (self.uri, l10nobject.uri)
    structure_diff = compare_structures(self, l10nobject)
    for pos, elem in enumerate(structure_diff):
        if elem[0] == 'insert' and 'added' in flags:
            chunk = {'flags':['added']}
            chunk['elements'] = l10nobject[elem[3]:elem[4]]
            chunk['prev'] = l10nobject.get_prev_elements(elem[3])
            chunk['next'] = self.get_next_elements(elem[2])
            l10nobject_diff.append(chunk)
        elif elem[0] == 'equal' and ('modified' in flags or 'unmodified' in flags):
            for i in range(0, elem[2]-elem[1]):
                key = (elem[1]+i, elem[3]+i)
                rec = (self[key[0]], l10nobject[key[1]])
                if isinstance(rec[0], unicode):
                    if values is False or rec[0]==rec[1]:
                        if 'unmodified' in flags:
                            chunk = {'flags': ['unmodified'], 'elements': rec[0]}
                        else:
                            continue
                    else:
                        if 'modified' in flags:
                            chunk = {'flags': ['modified'], 'elements': (rec[0], rec[1])}
                        else:
                            continue
                    chunk['prev'] = l10nobject.get_prev_elements(key[1])
                    chunk['next'] = self.get_next_elements(key[0]+1)
                elif isinstance(rec[0], Entity):
                    if values is True:
                        entity_diff = rec[0].diff(rec[1], struct=True)
                        if entity_diff.empty():
                            if 'unmodified' in flags:
                                chunk = {'flags': ['unmodified'], 'elements': rec[0]}
                            else:
                                continue
                        else:
                            if 'modified' in flags:
                                chunk = {'flags': ['modified'], 'elements': (rec[0].id, entity_diff)}
                            else:
                                continue
                    else:
                        if 'unmodified' in flags:
                            chunk = {'flags': ['unmodified'], 'elements': rec[0]}
                        else:
                            continue
                    chunk['prev'] = l10nobject.get_prev_elements(key[1])
                    chunk['next'] = self.get_next_elements(key[0]+1)
                elif isinstance(rec[0], Comment):
                    comment_diff = rec[0].diff(rec[1], flags=flags, values=values)
                    if comment_diff.empty():
                        if 'unmodified' in flags:
                            chunk = {'flags': ['unmodified'], 'elements': rec[0]}
                        else:
                            continue
                    else:
                        if 'modified' in flags:
                            chunk = {'flags': ['modified'], 'elements': ('comment', comment_diff)}
                        else:
                            continue
                    chunk['prev'] = l10nobject.get_prev_elements(key[1])
                    chunk['next'] = self.get_next_elements(key[0]+1)
                l10nobject_diff.append(chunk)
        elif elem[0] == 'replace' and 'replaced' in flags:
            chunk = {'flags': ['replaced']}
            chunk['elements'] = []
            chunk['elements2'] = []
            chunk['prev'] = l10nobject.get_prev_elements(elem[3])
            chunk['next'] = self.get_next_elements(elem[2])
            for i in range(0, elem[2]-elem[1]):
                chunk['elements'].append(self[elem[1]+i])
            for i in range(0, elem[4]-elem[3]):
                chunk['elements2'].append(l10nobject[elem[3]+i])
            l10nobject_diff.append(chunk)
        elif elem[0] == 'delete' and 'removed' in flags:
            chunk = {'flags': ['removed']}
            chunk['elements'] = self[elem[1]:elem[2]]
            chunk['prev'] = l10nobject.get_prev_elements(elem[3])
            chunk['next'] = self.get_next_elements(elem[2])
            l10nobject_diff.append(chunk)
    return l10nobject_diff

Structure.diff = l10nobject_diff

def apply_entitylist_diff(self, entitylist_diff):
    for i in entitylist_diff:
        if 'modified' in entitylist_diff[i]['flags']:
            for el in self:
                if isinstance(el, Entity) and el.id == i:
                    el.set_value(entitylist_diff[i]['elem'].value()[1])
        elif 'added' in entitylist_diff[i]['flags']:
            self.addEntity(entitylist_diff[i]['elem'])
        elif 'removed' in entitylist_diff[i]['type']:
            self.removeEntity(i)

Structure.apply_entitylist_diff = apply_entitylist_diff

def apply_l10nobject_diff (self, l10nobject_diff):
    if isinstance(l10nobject_diff, EntityListDiff):
        self.apply_entitylist_diff(l10nobject_diff)
        return
    for i in l10nobject_diff:
        if 'added' in i["flags"]:
            pos = self.locate_position(i['prev'], i['next'], chunk_size=len(i['elements']), mode='added')
            if pos != None:
                self[pos:pos] = i['elements']
        if 'modified' in i["flags"]:
            element = i['elements']
            if isinstance(element[1], EntityDiff):
                pos = self.get_entity_position(element[0])
                self[pos].apply_diff(element[1])
            elif isinstance(element[0], Comment):
                pos = self.locate_position(i['prev'], i['next'], chunk_size=len(i['elements']))
                self[pos] = element[1]
            elif isinstance(element[0], unicode):
                pos = self.locate_position(i['prev'], i['next'], chunk_size=len(i['elements']))
                if self[pos] == element[0]:
                    self[pos] = element[1]
        if 'replaced' in i["flags"]:
            pos = self.locate_position(i['prev'], i['next'], chunk_size=len(i['elements']))
            if pos != None:
                self[pos:pos+1] = i['elements2']
        if 'removed' in i['flags']:
            pos = self.locate_position(i['prev'], i['next'], chunk_size=len(i['elements']))
            self[pos:pos+len(i['elements'])] = []

Structure.apply_diff = apply_l10nobject_diff
