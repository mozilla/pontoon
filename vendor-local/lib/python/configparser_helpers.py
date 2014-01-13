#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import MutableMapping
try:
    from thread import get_ident
except ImportError:
    try:
        from _thread import get_ident
    except ImportError:
        from _dummy_thread import get_ident

# from reprlib 3.2.1
def recursive_repr(fillvalue=u'...'):
    u'Decorator to make a repr function return fillvalue for a recursive call'

    def decorating_function(user_function):
        repr_running = set()

        def wrapper(self):
            key = id(self), get_ident()
            if key in repr_running:
                return fillvalue
            repr_running.add(key)
            try:
                result = user_function(self)
            finally:
                repr_running.discard(key)
            return result

        # Can't use functools.wraps() here because of bootstrap issues
        wrapper.__module__ = getattr(user_function, u'__module__')
        wrapper.__doc__ = getattr(user_function, u'__doc__')
        wrapper.__name__ = getattr(user_function, u'__name__')
        wrapper.__annotations__ = getattr(user_function, u'__annotations__', {})
        return wrapper

    return decorating_function

# from collections 3.2.1
class _ChainMap(MutableMapping):
    u''' A ChainMap groups multiple dicts (or other mappings) together
    to create a single, updateable view.

    The underlying mappings are stored in a list.  That list is public and can
    accessed or updated using the *maps* attribute.  There is no other state.

    Lookups search the underlying mappings successively until a key is found.
    In contrast, writes, updates, and deletions only operate on the first
    mapping.

    '''

    def __init__(self, *maps):
        u'''Initialize a ChainMap by setting *maps* to the given mappings.
        If no mappings are provided, a single empty dictionary is used.

        '''
        self.maps = list(maps) or [{}]          # always at least one map

    def __missing__(self, key):
        raise KeyError(key)

    def __getitem__(self, key):
        for mapping in self.maps:
            try:
                return mapping[key]             # can't use 'key in mapping' with defaultdict
            except KeyError:
                pass
        return self.__missing__(key)            # support subclasses that define __missing__

    def get(self, key, default=None):
        return self[key] if key in self else default

    def __len__(self):
        return len(set().union(*self.maps))     # reuses stored hash values if possible

    def __iter__(self):
        return iter(set().union(*self.maps))

    def __contains__(self, key):
        return any(key in m for m in self.maps)

    @recursive_repr()
    def __repr__(self):
        return u'{0.__class__.__name__}({1})'.format(
            self, u', '.join(map(repr, self.maps)))

    @classmethod
    def fromkeys(cls, iterable, *args):
        u'Create a ChainMap with a single dict created from the iterable.'
        return cls(dict.fromkeys(iterable, *args))

    def copy(self):
        u'New ChainMap or subclass with a new copy of maps[0] and refs to maps[1:]'
        return self.__class__(self.maps[0].copy(), *self.maps[1:])

    __copy__ = copy

    def new_child(self):                        # like Django's Context.push()
        u'New ChainMap with a new dict followed by all previous maps.'
        return self.__class__({}, *self.maps)

    @property
    def parents(self):                          # like Django's Context.pop()
        u'New ChainMap from maps[1:].'
        return self.__class__(*self.maps[1:])

    def __setitem__(self, key, value):
        self.maps[0][key] = value

    def __delitem__(self, key):
        try:
            del self.maps[0][key]
        except KeyError:
            raise KeyError(u'Key not found in the first mapping: {!r}'.format(key))

    def popitem(self):
        u'Remove and return an item pair from maps[0]. Raise KeyError is maps[0] is empty.'
        try:
            return self.maps[0].popitem()
        except KeyError:
            raise KeyError(u'No keys found in the first mapping.')

    def pop(self, key, *args):
        u'Remove *key* from maps[0] and return its value. Raise KeyError if *key* not in maps[0].'
        try:
            return self.maps[0].pop(key, *args)
        except KeyError:
            raise KeyError(u'Key not found in the first mapping: {!r}'.format(key))

    def clear(self):
        u'Clear maps[0], leaving maps[1:] intact.'
        self.maps[0].clear()
