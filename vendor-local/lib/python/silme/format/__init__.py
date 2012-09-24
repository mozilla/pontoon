import os

class Manager(object):
    formats = {}
    names = {}

    @classmethod
    def register(cls, *args):
        """
        register for Manager
        """
        for fp in args:
            if isinstance(fp, str):
                if fp in cls.names:
                    continue
                module = __import__(fp, globals(), locals(), [], 1)
                module.register(cls)
            else:
                for ext in fp.extensions:
                    cls.formats[ext.lower()] = fp
                name = fp.__module__
                cls.names[name[name.rfind('.')+1:]] = fp

    @classmethod
    def register_all(cls):
        dir = os.path.dirname(__file__)
        list = os.listdir(dir)
        modules = [f for f in list if os.path.isdir(os.path.join(dir, f))]
        for name in modules:
            try:
                module = __import__(name, globals(), locals(), [], 1)
                module.register(cls)
            except:
                pass

    @classmethod
    def get(cls, name=None, path=None):
        if name:
            if name in cls.names:
                return cls.names[name]
            else:
                try:
                    module = __import__(name, globals(), locals(), [], 1)
                except ImportError:
                    raise KeyError ('no matching format')
                module.register(cls)
                return cls.names[name]
        elif path:
            if path.find('.') != -1:
                ext = os.path.splitext(path.lower())[1][1:]
            else:
                ext = path.lower()
            if ext in cls.formats:
                return cls.formats[ext]
        raise KeyError('no matching parser')
