"""
silme.core.EntityList is a list of entities.
"""

class EntityList(dict):
    uri = None
    id = None
    _keys = None

    def __init__(self, id=None, elist=None, order=True):
        """
        id - id for EntityList
        list - list of entities to add to EntityList
        order - if EntityList should keep entities order according to the order
                in which they were added
        """
        dict.__init__(self)
        self.fallback = []
        if id:
            self.id = id
        if elist:
            if isinstance(elist, list):
                map(self.add, elist)
            elif isinstance(elist, dict):
                map(self.add, elist.values())
            else:
                raise ValueError('could not assign list')
        if order:
            self._keys = [] 

    def _custom_iter(self):
        for i in self._keys:
            yield i

    def __iter__(self):
        if self._keys is None:
            return dict.__iter__(self)
        else:
            return self._custom_iter()

    def __repr__(self):
        """Prints entity debug text representation."""
        if len(self) == 0:
            return '<entitylist: "%s">' % self.id
        else:
            keys = self.keys()
            string = '<entitylist: "%s" [%s]>' % \
                (self.id,', '.join(('<entity: "%s">' % i) for i in keys))
            return string

    def __setitem__(self, key, value):
        """Adds new entity to EntityList"""
        super(EntityList, self).__setitem__(key, value)
        try:
            self._keys.append(key)
        except AttributeError: # _keys is not set
            pass

    def __delitem__(self, id):
        """Removes entity with given id from EntityList."""
        super(EntityList, self).__delitem__(id)
        try:
            self._keys.remove(id)
        except ValueError:  # _keys is not set
            pass
    remove_entity = __delitem__

    def add(self, entity):
        """Adds new entity to EntityList"""
        super(EntityList, self).__setitem__(entity.id, entity)
        try:
            self._keys.append(entity.id)
        except AttributeError: # _keys is not set
            pass
    add_entity = add

    def get(self, id):
        return self[id]
    entity = get

    def has_entity(self, id): return self.has_key(id)

    def entities(self):
        """Returns a list of all entities from EntityList."""
        if self._keys is None:
            return self
        else:
            return dict([(i,self[i]) for i in self._keys])

    def keys(self):
        """Returns all entity ids from EntityList."""
        if self._keys is None:
            return dict.keys(self)
        else:
            return self._keys
    ids = keys

    def modify(self, id, value, code='default'):
        """Modifies entity value in EntityList, optionally with given locale code."""
        self[id].set_value(value, code)
        return True
    modify_entity = modify

    def value(self, id, fallback=None):
        """Returns entity value from EntityList.
        
        fallback -- list of locale codes to try when getting value from entity.
        """
        if fallback == None and self.fallback:
            return self[id].get_value(self.fallback)
        return self[id].get_value(fallback)

    def locale_codes(self):
        """Returns list of locale codes existing in entities in EntityList."""
        locales = []
        for entity in self.values():
            for key in entity.value.keys():
                if key not in locales:
                    locales.append(key)
        return locales

    def locales(self, localelist):
        """Returns a new EntityList filtered to entities with locale codes listed in localelist argument."""
        elist = EntityList()
        elist.id = self.id
        elist.uri = self.uri
        elist._keys = self._keys
        elist.fallback = self.fallback
        for entity in self.values():
            elist.add_entity(entity.get_locales(localelist))
        return elist

    def merge(self, elist):
        """Merges one EntityList with another."""
        for entity in elist:
            if self.has_key(entity.id):
                self[entity.id].merge(entity)
            else:
                self[entity.id] = entity
