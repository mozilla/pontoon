from silme.core.types.odict import OrderedDict
from silme.core.types import LazyDict as LazyDict

from abc import ABCMeta

class FactoryMeta(type):
    def __new__(cls, *args, **kwargs):
        return cls

_types = {
    'ordered': [OrderedDict, 'Ordered', False],
    'lazy': [LazyDict, 'Lazy', False],
    }


class LazyDictMeta(ABCMeta, type):
    def __call__(cls, *args, **kwargs):
        classes = [cls]
        name = []
        attrs = []
        for key in _types:
            t = _types[key]
            r = kwargs.pop(key, t[2])
            if r:
                classes.append(t[0])
                name.append(t[1])
            attrs.append((key, r))
        t = type('%s%s' % (''.join(name), cls.__name__),
                 tuple(classes),
                 {})
        cl = t.__new__(t, *args, **kwargs)
        cl.__init__(*args, **kwargs)
        for attr in attrs:
            setattr(cl, attr[0], attr[1])
        return cl

# metaclass for py2 and py3
ComplexDict = LazyDictMeta('ComplexDict', (dict, ), {})

