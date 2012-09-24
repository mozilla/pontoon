from silme.core.entity import Entity
from silme.core.list import EntityList


class Blob(object):
    uri = None
    id = None
    source = None


class Structure(list, Blob):
    process_cb = None
    fallback = None
    params = {}

    def __init__(self, id=None):
        """
        L10nStruture can be initialized with optional argument: id
        """
        list.__init__(self)
        Blob.__init__(self)
        self.id = id

    def __getitem__(self, key):
        if isinstance(key, int):
            return list.__getitem__(self, key)
        else:
            for item in self:
                if isinstance(item, Entity) and item.id == key:
                    return item
            raise KeyError()

    def _get_pos(self, pos):
        """
        It is an internal method for translating tuple in form of:
        ('before', 'entity.id') or ('after', 'entity.id')
        which are returned internally by our methods into a solid number.
        
        If pos is a number it will just be returned as integer.
        """
        if isinstance(pos, tuple):
            p = self.entity_pos(pos[1])
            return p + 1 if pos[0] == 'after' else p
        else:
            return int(pos)

    def add_at_pos(self, element, pos=None):
        """
        adds an element to L10nObject.
        pos - if given, allows you to decide where the element will be added
           pos may be in form of an integer or a tuple like ('before', 'entity.id'), ('after', 'entity.id')
        """
        if pos is None:
            self.append(element)
        else:
            self.insert(self._get_pos(pos), element)

    def add_entity(self, entity, pos=None):
        """
        adds an entity to L10nObject
        pos - if given, allows you to decide where the entity will be added
        """
        self.add_at_pos(entity, pos)
        return 1

    def value(self, id, fallback=None):
        """
        returns a value of an entity with given id
        fallback - if given overrides default locale fallback (e.g. ['de', 'fr', 'en-US'])
        
        if given entity does not exist it will raise a KeyError
        """
        if fallback == None and self.fallback:
            fallback = self.fallback
        return self.entity(id).get_value(fallback)

    def locale_codes(self):
        """
        returns list of locale codes existing in L10nObject
        """
        locales = []
        for entity in self.entities().values():
            for key in entity._value.keys():
                if key not in locales:
                    locales.append(key)
        return locales

    def keys(self):
        """
        returns list of id's of entities in L10nObject
        """
        return [item.id for item in self if isinstance(item, Entity)]
    ids = keys

    def entities(self, path=None):
        """
        returns all entities from L10nObject
        """
        if path is None:
            return dict([(item.id,item)
                         for item in self if isinstance(item, Entity)])
        else:
            spath = '%s/%s' % (path, self.id) if path else self.id
            return dict([(item.id, (item, spath)) for item in self if isinstance(item, Entity)])
            

    def __contains__(self, id):
        """
        returns True if entity with given id exists or False otherwise
        """
        for item in self:
            if isinstance(item, Entity) and item.id == id:
                return True
        return False
    has_entity = __contains__

    def modify_entity(self, id, value, code=None):
        """
        modifies entity value
        code - if given modified the value for given locale code
        """
        for item in self:
            if isinstance(item, Entity) and item.id == id:
                item.set_value(value, code)
                return True
        raise KeyError('No such entity')

    def entity(self, id):
        """
        returns an entity for a given id
        """
        for item in self:
            if isinstance(item, Entity) and item.id == id:
                return item
        raise KeyError('No such entity')

    def entity_pos(self, id):
        """
        returns position of entity in L10nObject
        """
        for (i, item) in enumerate(self):
            if isinstance(item, Entity) and item.id == id:
                return i
        raise KeyError('No such entity')

    def remove_entity(self, id):
        """
        removes entity for given id or raises KeyError
        """
        for (num, item) in enumerate(self):
            if isinstance(item, Entity) and item.id == id:
                del self[num]
                return True
        raise KeyError('No such entity')

    def add_comment(self, comment, pos=None):
        self.add_at_pos(comment, pos)
        return 1

    def add_string(self, string, pos=None):
        self.add_at_pos(string, pos)
        return 1

    def add(self, element, pos=None):
        """
        adds an element (string, entity or comment) to l10nObject
        pos - if given addes an element at given position
        
        returns a number representing how many new elements have been added
          Usually one, but if a new string gets added and is concatanated to previous/next one
          the value will be 0.
        """
        if element == None:
            return 0
        t = type(element).__name__[0]
        if t == 's' or t == 'u': # s - str, u - unicode
            return self.add_string(element, pos)
        elif t == 'E': # E - Entity
            return self.add_entity(element, pos)
        elif t == 'C': # C - Comment
            return self.add_comment(element, pos)
        else:
            raise Exception('Cannot add element of type "' + type(element).__name__ +
                            '" to L10nObject')

    def add_elements(self, sequence, pos=None):
        """
        adds set of elements
        pos - if given addes the elements at given position
        
        returns a number representing how many new elements have been added
          Usually the number will be equal the number of 
        """
        it = iter(sequence)
        tshift = 0
        if not pos == None:
            pos = self._get_pos(pos)
        while True:
            try:
                shift = self.add(it.next(), pos=(None if pos == None else pos+tshift))
                tshift += shift
            except StopIteration:
                break
        return tshift

    def remove_element(self, pos):
        """
        removes an element at given position from the L10nObject
        """
        del self[pos]

    def element(self, position):
        return self[position]

    def entitylist(self):
        """
        returns an ElementList representation of the L10nObject
        """
        entityList = EntityList()
        entityList.id = self.id
        entityList.fallback = self.fallback
        for entity in self.entities().values():
            entityList.add(entity)
        return entityList

    def process(self):
        """
        launches a process function on the L10nObject if
        processing method is provided
        """
        try:
            return self.process_cb(self)
        except TypeError:
            raise Exception('process callback function not specified')

    def locales(self, localelist):
        """
        returns a clone of L10nObject with entities only
        in given list of locales
        """
        l10n_object = Structure()
        l10n_object.id = self.id
        l10n_object.uri = self.uri
        l10n_object.fallback = localelist
        l10n_object.source = self.source
        for element in self:
            if isinstance(element, Entity):
                l10n_object.add_entity(element.locales(localelist))
            else:
                l10n_object.add(element)
        return l10n_object

    def merge(self, l10n_object):
        """
        merges L10nObject with another L10nObject (only entities)
        """
        for entity in l10n_object.entities().values():
            if entity.id in self:
                self.entity(entity.id).merge(entity)
            else:
                self.add_entity(entity)
        if l10n_object.fallback:
            for code in l10n_object.fallback:
                if code not in self.fallback:
                    self.fallback.append(code)


class Comment(Structure):
    """
    Comment class is a sub-class of L10nObject but cannot
    take Comment as an element.
    
    It means that by default Comments store strings and Entities.
    """
    def __init__(self, elist=None):
        Structure.__init__(self)
        if elist:
            for i in elist:
                self.add(i)
    
    def __repr__(self):
        string = '<comment: '
        for i in self:
            string += unicode(i)
        string += '>'
        return string

    def add(self, element, pos=None):
        if isinstance(element, Comment):
            raise Exception('Cannot add comment to comment')
        return Structure.add(self, element, pos)
