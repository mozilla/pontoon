import os

class Manager(object):
    clients = {}

    @classmethod
    def register(cls, *args):
        for client in args:
            if isinstance(client, str):
                if client in cls.clients:
                    continue
                module = __import__(client, globals(), locals(), [], 1)
                module.register(cls)
            else:
                cls.clients[client.name] = client

    @classmethod
    def register_all(cls):
        dir = os.path.dirname(__file__)
        list = os.listdir(dir)
        modules = [f for f in list if os.path.isfile(os.path.join(dir, f))]
        for name in modules:
            name = name[:name.rfind('.')]
            try:
                module = __import__(name, globals(), locals(), [], 1)
                module.register(cls)
            except:
                pass

    @classmethod
    def get(cls, name=None, path=None):
        if name:
            ext = name.lower()
            if ext in cls.clients:
                return cls.clients[ext]
            else:
                try:
                    module = __import__(name, globals(), locals(), [], 1)
                except ImportError: 
                    raise Exception('no matching ioclient')
                module.register(cls)
                return cls.clients[ext]
        elif path:
            for client in cls.clients.values():
                if client.matches_path(path):
                    return client
            raise Exception('no matching ioclient')
