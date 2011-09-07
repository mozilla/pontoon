'''
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

'''
from functools import partial
from collections import MutableMapping, ItemsView, ValuesView
import datetime

__all__ = ["LazyDict",]

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
        super(LazyDict, self).__init__(*args, **kwargs)

    def __cmp__(self, other):
        self.resolve()
        return super(LazyDict, self).__cmp__(other)

    def __eq__(self, other):
        self.resolve()
        return super(LazyDict, self).__eq__(other)

    def __setitem__(self, key, item):
        self._stubs.discard(key)
        super(LazyDict, self).__setitem__(key, item)

    def __getitem__(self, key):
        if key in self._stubs:
            super(LazyDict, self).__setitem__(key,
                                              super(LazyDict, self).__getitem__(key)())
            self._stubs.remove(key)
        return super(LazyDict, self).__getitem__(key)

    def __delitem__(self, key):
        self._stubs.discard(key)
        super(LazyDict, self).__delitem__(key)

    def clear(self):
        self._stubs.clear()
        super(LazyDict, self).clear()

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
        v = partial(rslv if rslv else self._resolver,
                            key, *args, **kwargs)
        super(LazyDict, self).__setitem__(key, v)

    def resolve(self):
        """
        Resolves all stubs
        """
        for k in self._stubs:
            super(LazyDict, self).__setitem__(k,
                    super(LazyDict, self).__getitem__(k)())
        self._stubs.clear()

    def set_resolver(self, resolver):
        """
        Sets the default stub resolver
        """
        self._resolver = resolver


class LazyDictDebug(LazyDict):
    """
    This class can be used instead of LazyDict to analyze if the code
    base usage make stubs valuable
    """
    def __init__(self, *args, **kwargs):
        super(LazyDictDebug, self).__init__(*args, **kwargs)
        self.stats = {'realitems': 0, 'stubs': 0, 'resolved': 0}
        self.timers = {}

    def __missing__(self, key):
        try:
            stub = self._stubs.pop(key)
        except KeyError:
            raise KeyError(key)
        s = stub()
        dict.__setitem__(self, key, s)
        return s

    def __setitem__(self, key, item):
        self.stats['realitems'] += 1
        LazyDict.__setitem__(self, key, item)

    def set_stub(self, key, resolver, *args, **kwargs):
        self.stats['stubs']+=1
        LazyDict.set_stub(self, key, resolver, *args, **kwargs)

    def get_stats(self):
        stats = self.stats
        if len(self.timers):
            stats['time_cost'] = sum(self.timers.values(), 0.0) / len(self.timers)
        return stats

    def __missing__(self, key):
        self.stats['resolved']+=1
        t1 = datetime.datetime.now()
        LazyDict.__missing__(self, key)
        t2 = datetime.datetime.now()
        tdiff = t2 - t1
        self.timers[key] = tdiff.microseconds

