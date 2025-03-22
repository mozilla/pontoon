import six
try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle  # type: ignore

__all__ = ('long', 'pickle', 'unicode')

if six.PY3:
    long = int
    unicode = str
else:
    long = long
    unicode = unicode
