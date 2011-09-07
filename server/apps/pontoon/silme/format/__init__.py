import os
import sys

class Manager(object):
    formats = {}
    names = {}
    path = []

    @classmethod
    def _import(cls, fp):
        added = list(set(cls.path).difference(sys.path))
        sys.path = added + sys.path # we want to have the locally added in front
        module = __import__(fp, globals(), locals(), [], 1)
        sys.path = list(set(sys.path).difference(added))
        return module

    @classmethod
    def register(cls, *args):
        """
        register for Manager
        """
        for fp in args:
            if isinstance(fp, str):
                if fp in cls.names:
                    continue
                module = cls._import(fp)
                module.register(cls)
            else:
                for ext in fp.extensions:
                    cls.formats[ext.lower()] = fp
                name = fp.name
                cls.names[name] = fp

    @classmethod
    def register_all(cls):
        dir = os.path.dirname(__file__)
        list = os.listdir(dir)
        modules = [f for f in list if os.path.isdir(os.path.join(dir, f))]
        for name in modules:
            try:
                module = cls._import(name)
                module.register(cls)
            except:
                pass
    
    @classmethod
    def get(cls, name=None, path=None):
        if name:
            try:
                return cls.names[name]
            except KeyError:
                try:
                    module = cls._import(name)
                except ImportError:
                    raise KeyError ('no matching format')
                return module.FormatParser()
        elif path:
            try:
                return cls.formats[os.path.splitext(path)[1][1:].lower()]
            except KeyError:
                pass
        raise KeyError('no matching parser')
