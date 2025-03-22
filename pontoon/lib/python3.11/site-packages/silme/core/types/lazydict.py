"""
LazyDict is a subclass of a dict that can additionally store
items in a form of a stub that is expanded on the first call.

Such class may be useful in all cases where dictionary items
are expensive to initialize and on average an application
is using only some of the elements of the dictionary.

Example:

    def resolver(self, key, *args, **kwargs):
        print("resolving")
        table = kwargs.pop('table', None)
        return QueryValue(table=table)

    d = LazyDict({'a': 1})
    d.set_stub('b', resolver, table='items')

    print(len(d))                    # 2
    x = d['b']                       # resolving
    x2 = d['b']                      #
    print(isinstance(x2, QueryValue) # True

"""
from functools import partial
from collections.abc import MutableMapping, ItemsView, ValuesView

__all__ = [
    "LazyDict",
]


class LazyItemsView(ItemsView):
    def __iter__(self):
        self._mapping.resolve()
        for key in self._mapping:
            yield (key, self._mapping[key])


class LazyValuesView(ValuesView):
    def __iter__(self):
        self._mapping.resolve()
        for key in self._mapping:
            yield self._mapping[key]


class LazyDict(dict):
    _resolver = None

    def __init__(self, *args, **kwargs):
        self._stubs = set()
        super().__init__(*args, **kwargs)

    def __cmp__(self, other):
        self.resolve()
        return super().__cmp__(other)

    def __eq__(self, other):
        self.resolve()
        return super().__eq__(other)

    def __setitem__(self, key, item):
        self._stubs.discard(key)
        super().__setitem__(key, item)

    def __getitem__(self, key):
        if key in self._stubs:
            super().__setitem__(key, super().__getitem__(key)())
            self._stubs.remove(key)
        return super().__getitem__(key)

    def __delitem__(self, key):
        self._stubs.discard(key)
        super().__delitem__(key)

    def clear(self):
        self._stubs.clear()
        super().clear()

    def copy(self):
        x = self.__class__(self)
        x._stubs = self._stubs.copy()
        return x

    get = MutableMapping.get
    update = MutableMapping.update
    popitem = MutableMapping.popitem
    setdefault = MutableMapping.setdefault
    __repr__ = MutableMapping.__repr__

    def items(self):
        return LazyItemsView(self)

    def values(self):
        return LazyValuesView(self)

    __marker = object()

    def pop(self, key, default=__marker):
        try:
            value = self[key]
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            del self[key]
            return value

    def set_stub(self, key, rslv=None, *args, **kwargs):
        """
        Adds a stub of an element. It takes a callable rslv
        that will be called when the item is requested
        for the first time.

        If rslv is None, LazyDict will try to use default resolver
        provided by set_default_resolver.
        """
        self._stubs.add(key)
        v = partial(rslv if rslv else self._resolver, key, *args, **kwargs)
        super().__setitem__(key, v)

    def resolve(self):
        """
        Resolves all stubs
        """
        for k in self._stubs:
            super().__setitem__(k, super().__getitem__(k)())
        self._stubs.clear()

    def set_resolver(self, resolver):
        """
        Sets the default stub resolver
        """
        self._resolver = resolver
