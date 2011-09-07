"""
Structures are data objects that represent the storage data structures that
are used to store localization data, like files or database records.

The main use case for a Structure is when a developer wants to preserve the
exact same format in which the data was stored while working on the data,
and later save the modified version keeping the exact same structure.

An example when Structure makes much more sense than EntityList is when a
developer wants to load a file, add new entities, and save it back.
On the other hand, if the entities are loaded in order to be only presented
to the user, or for any statistical reasons - EntityList is much lighter.

A Structure is a in-memory representation of a whole localization unit, an
EntityList is a representation of the entities from the unit.
"""


from silme.core.entity import Entity, is_entity, is_string
from silme.core.list import EntityList
from functools import partial


class Blob(object):
    """
    A Blob is a data stream that is not localizable, but may be
    a part of a package of structures.

    An example may be an image file in a localization directory, or
    a file in a format that has not been available.

    The main use case for the class is to preserve the non-translatable
    data in a in-memory representation of a package (a directory etc.)
    """
    uri = None
    id = None
    source = None

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)


class Structure(list, Blob):
    """
    A Structure is a localization grouping unit, like a file, or a table,
    that contains a set of entities and additional elements like comments,
    white spaces and/or others.

    The main use case for a Structure is to load a file into a memory,
    edit it, and save it back preserving as much of the file structure as
    possible which in turn may be important for all VCS's based workflows.
    """
    _process_cb = None  # process callback function

    def __init__(self, id):
        self.id = id

    def __getitem__(self, key):
        if type(key) == int:
            return list.__getitem__(self, key)
        else:
            return self.entity(key)

    def _get_pos(self, pos):
        """An internal method for translating a relative pointer like:
        ('before', 'entity.id') or ('after', 'entity.id') into an index.

        A relative pointer must be a two element tuple where the first
        element is a string "before" or "after" and the second is
        an id of an entity that is already in the structure.

        If pos is a number it will just be returned as an integer.
        """
        if type(pos) == tuple:
            p = self.entity_pos(pos[1])
            return p + 1 if pos[0] == 'after' else p
        elif pos is None:
            return None
        else:
            return int(pos)

    def add_at_pos(self, element, pos=None):
        """adds an element to the Structure.
        pos - if given, allows decide where the element will be added
           pos may be in form of an integer or a relative pointer like
           ('before', 'entity.id'), ('after', 'entity.id')
        """
        if pos is None:
            self.append(element)
        else:
            self.insert(self._get_pos(pos), element)

    def add_entity(self, entity, pos=None):
        """adds an entity to the Structure
        pos - if given, allows decide where the entity will be added
           pos may be in form of an integer or a relative pointer like
           ('before', 'entity.id'), ('after', 'entity.id')
        """
        self.add_at_pos(entity, pos)
        return 1

    def value(self, id):
        """returns a value of an entity with given id

        if the given entity does not exist, KeyError will be raised
        """
        return self.entity(id).value

    def keys(self):
        """returns a list of id's of entities from the Structure
        """
        return [item.id for item in self if isinstance(item, Entity)]
    ids = keys

    def entities(self):
        """
        Returns a list of entities from the structure
        """   
        return [item for item in self if is_entity(item)]

    def entitylist(self):
        """Returns an EntityList object with entities from the Structure.
        """
        return EntityList(self.id,
                          *[item for item in self if is_entity(item)])

    def entities_with_path(self, path_prefix):
        """Returns a dict of all entities from the Structure in a form of
        d[entity.id] = (entity, path)
        """
        spath = '%s/%s' % (path_prefix, self.id) if path_prefix else self.id
        return dict([(item.id,
                     (item, spath)) for item in self if is_entity(item)])

    def __contains__(self, id):
        """returns True if an entity with given id exists
        """
        for item in self:
            if is_entity(item) and item.id == id:
                return True
        return False
    has_entity = __contains__

    def modify_entity(self, id, value):
        """modifies an entity value
        """
        for item in self:
            if is_entity(item) and item.id == id:
                item.value = value
                return True
        raise KeyError('No such entity')

    def entity(self, id):
        """returns an entity for a given id
        """
        for item in self:
            if is_entity(item) and item.id == id:
                return item
        raise KeyError('No such entity')

    def entity_pos(self, id):
        """returns the position of an entity in the Structure
        """
        for i, item in enumerate(self):
            if is_entity(item) and item.id == id:
                return i
        raise KeyError('No such entity')

    def remove_entity(self, id):
        """removes an entity for the given id or raises KeyError
        """
        for i, item in enumerate(self):
            if is_entity(item) and item.id == id:
                del self[i]
                return True
        raise KeyError('[%s] No such entity: %s' % (self.id, id))

    def add_comment(self, comment, pos=None):
        self.add_at_pos(comment, pos)
        return 1

    def add_string(self, string, pos=None):
        self.add_at_pos(string, pos)
        return 1

    def add(self, item, pos=None):
        """adds an element (string, entity or comment) to the Structure
        pos - if given addes an element at given position

        returns a number representing how many new elements have been added
          Usually one, but if a new string gets added and is concatanated
          to previous/next one the value will be 0.
        """
        if is_string(item):  # string
            return self.add_string(item, pos)
        elif is_entity(item):  # Entity
            return self.add_entity(item, pos)
        elif isinstance(item, Comment):  # Comment
            return self.add_comment(item, pos)
        elif item is None:
            return 0
        else:
            raise Exception('Cannot add element of type "' +
                            type(item).__name__ +
                            '" to the Structure')

    def add_elements(self, sequence, pos=None):
        """
        adds a set of elements
        pos - if given addes the elements at given position

        returns a number representing how many new elements have been added
        Usually the number will be equal to the number of added elements,
        but if a new string gets added and is concatanated
          to previous/next one the return value will be lower.
        """
        shift = 0
        if isinstance(sequence, dict):
            sequence = sequence.values()
        pos = self._get_pos(pos)
        #a=a[:2]+b+a[2:] ?
        for i in sequence:
            shift += self.add(i, pos=(None if pos is None else pos + shift))
        return shift

    remove_element = list.__delitem__

    element = list.__getitem__

    def process(self):
        """
        launches a process function on the Structure if
        processing method is provided
        """
        try:

            return self._process_cb()
        except TypeError:
            raise Exception('process callback function not specified')

    def set_process_cb(self, cb):
        self._process_cb = partial(cb, self)
        return True


class Comment(Structure):
    """
    Comment class is a sub-class of a Structure but cannot
    take a Comment as an element.

    It means that by default Comments store strings and Entities.
    """

    def __init__(self):
        self.id = None

    def __repr__(self):
        string = '<comment: '
        for i in self:
            string += unicode(i)
        string += '>'
        return string

    def add(self, element, pos=None):
        if isinstance(element, Comment):
            raise Exception('Cannot add a comment to a comment')
        return Structure.add(self, element, pos)
