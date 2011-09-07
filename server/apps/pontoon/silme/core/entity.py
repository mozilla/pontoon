"""
silme.core.Entity represents a single localizable unit. Every entity is made
of a unique identifier (id) and a value that may be simple - a string, number,
url etc. or more complex - for example a dictionary of values.

On top of that, entities may contain various parameters and attributes that
may be specific to the given localization format and should be represented
by subclasses of Entity class, and possibly one of the Value classes.

By default silme.core.Value returns one of its more specific subclasses.
"""
import copy
from silme.core.types.odict import OrderedDict

__all__ = ['is_string', 'string', 'is_entity', 'Entity']

try:
    basestring
    string = unicode

    def is_string(v):
        """
        Tests if the argument is a string
        """
        return isinstance(v, basestring)
except:
    string = str

    def is_string(v):
        """
        Tests if the argument is a string
        """
        return isinstance(v, str)


def is_entity(v):
    """
    Is the argument an entity
    """
    return isinstance(v, Entity)


class Value(object):
    def __new__(cls, *args, **kwargs):
        #if cls is not Value:
        #    return object.__new__(cls)
        try:
            i = args[0]
        except IndexError:
            raise Exception("hey! I need an arg to pick the right thing :))")
        if is_string(i):
            return SimpleValue(args[0])
        else:
            t = type(i)
            if issubclass(t, list):
                return ListValue(*args, **kwargs)
            elif issubclass(t, dict):
                return DictValue(*args, **kwargs)
            else:
                return ComplexValue(*args, **kwargs)


class SimpleValue(string, Value):
    """
    A simple, string based value for an entity
    """
    def get(self, *args, **kwargs):
        return self

    def __setitem__(self, key, value):
        raise TypeError("'%s' object does not support item assignment" %
                        type(self).__name__)

    def __getitem__(self, key):
        raise TypeError("'%s' object is unsubscriptable" %
                        type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("'%s' object does not support item deletion" %
                        type(self).__name__)


class ComplexValue(Value):
    """
    Entity value that is more complex than a single string
    """

    def __init__(self, value):
        self._value = value

    def get(self, val=None, *args, **kwargs):
        if val is None:
            val = self._value
        t = type(val)
        if is_string(val):
            return val
        elif t is list or t is tuple:
            return self.get(val[0])
        elif issubclass(t, dict):
            return self.get(list(val.values())[0])
        elif issubclass(t, set):
            return list(val)[0]
        else:
            return val

class ListValue(list, ComplexValue):
    """
    A value that is a list of values
    """

    def get(self, i=0, *args, **kwargs):
        return self[i]


class DictValue(OrderedDict, ComplexValue):
    """
    A value that is a dictionary of values
    """
    def get(self, key=None, *args, **kwargs):
        if key is not None:
            return self[key]
        return list(self.values())[0]


class Entity(object):
    """
    An entity is a basic localization data unit with a unique id and a value

    An ID represents a handler which a developer uses to call for the given
    entity and a value is any sort of localizable data bound to that id.
    """
    _select_value = None

    def __init__(self, id, value=None):
        self.id = id
        self.params = {}
        if value is not None:
            if isinstance(value, Value):
                self._value = value
            else:
                self._value = Value(value)
        else:
            self._value = None

    def __repr__(self):
        return '<entity: "%s">' % self.id

    def get_value(self, *args, **kwargs):
        """
        Returns a single value option (almost always it will be a string)
        basing on the class-defined mechanism and arguments passed to this
        method.

        One can customize the return mechanism by defining custom
        _select_value method for the object.
        """
        if self._select_value is not None:
            return self._select_value(self._value, *args, **kwargs)
        try:
            return self._value.get(*args, **kwargs)
        except AttributeError:
            return None

    def set_value(self, value, *args, **kwargs):
        if isinstance(value, Value):
            self._value = value
        else:
            self._value = Value(value)

    value = property(get_value, set_value)

    def __setitem__(self, key, value):
        self._value[key] = value

    def __getitem__(self, key):
        return self._value[key]

    def __delitem__(self, key):
        del self._value[key]

    @property
    def values(self):
        return copy.copy(self._value)

