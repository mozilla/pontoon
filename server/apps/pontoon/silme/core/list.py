"""
silme.core.EntityList is a data structure that represents a basic structure
that organizes entities into a list.

Usually entities inside a single entity list are related to each other by
a common theme or may be used together in a single UI piece.

Entity ids must be unique accross an entity list in which they are stored.
"""

from silme.core.types import ComplexDict


def is_entitylist(obj):
    """
    Tests if the argument is an EntityList object
    """
    return isinstance(obj, EntityList)


class EntityList(ComplexDict):
    """
    EntityList is a list of entities bundled together.
    """
    uri = None

    def __init__(self, id, *args, **kwargs):
        self.id = id
        super(EntityList, self).__init__()
        for i in args:
            if is_entitylist(i):
                for entity in i.entities():
                    self.add(entity)
            else:
                self.add(i)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, tuple(self.keys()))

    def add(self, entity):
        """Adds new entity to EntityList"""
        self[entity.id] = entity

    def modify(self, id, value):
        """Modifies entity value in EntityList,
        optionally with given locale code."""
        self[id].set_value(value)
        return True

    def entities(self):
        """Returns a list of all entities from EntityList."""
        return list(self.values())

    def value(self, id):
        """Returns entity value from EntityList.
        """
        return self[id].value


class ValueList(EntityList):
    """
    ValueList is a list of entity values - similar to EntityList but with an
    intention to store only the values of entities.
    """
    def __init__(self, id, *args, **kwargs):
        super(ValueList, self).__init__(id, *args, **kwargs)

    def add(self, entity):
        """Adds new entity to the ValueList"""
        self[entity.id] = entity.value

    def modify(self, id, value):
        """Modifies entity value in ValueList,
        optionally with given locale code."""
        self[id] = value
        return True

    def entities(self):
        """Raises a TypeError since ValueList does not support this method"""
        raise TypeError("'%s' object does not support entities method" %
                        type(self).__name__)

    def value(self, id):
        """Returns entity value from the ValueList
        This method is kept for parity with EntityList
        """
        return self[id]
