from collections import defaultdict
from uhashring import HashRing

from bmemcached.client import SOCKET_TIMEOUT
from bmemcached.client.mixin import ClientMixin
from bmemcached.compat import pickle


class DistributedClient(ClientMixin):
    """This is intended to be a client class which implement standard cache interface that common libs do...

    It tries to distribute keys over the specified servers using `HashRing` consistent hash.
    """
    def __init__(self, servers=('127.0.0.1:11211',), username=None, password=None, compression=None,
                 socket_timeout=SOCKET_TIMEOUT, pickle_protocol=0, pickler=pickle.Pickler, unpickler=pickle.Unpickler,
                 tls_context=None):
        super(DistributedClient, self).__init__(servers, username, password, compression, socket_timeout,
                                                pickle_protocol, pickler, unpickler, tls_context)
        self._ring = HashRing(self._servers)

    def _get_server(self, key):
        return self._ring.get_node(key)

    def delete(self, key, cas=0):
        """
        Delete a key/value from server. If key does not exist, it returns True.

        :param key: Key's name to be deleted
        :param cas: CAS of the key
        :return: True in case o success and False in case of failure.
        """
        server = self._get_server(key)
        return server.delete(key, cas)

    def delete_multi(self, keys):
        servers = defaultdict(list)
        for key in keys:
            server_key = self._get_server(key)
            servers[server_key].append(key)
        return all([server.delete_multi(keys_) for server, keys_ in servers.items()])

    def set(self, key, value, time=0, compress_level=-1):
        """
        Set a value for a key on server.

        :param key: Key's name
        :type key: str
        :param value: A value to be stored on server.
        :type value: object
        :param time: Time in seconds that your key will expire.
        :type time: int
        :param compress_level: How much to compress.
            0 = no compression, 1 = fastest, 9 = slowest but best,
            -1 = default compression level.
        :type compress_level: int
        :return: True in case of success and False in case of failure
        :rtype: bool
        """
        server = self._get_server(key)
        return server.set(key, value, time, compress_level)

    def set_multi(self, mappings, time=0, compress_level=-1):
        """
        Set multiple keys with it's values on server.

        :param mappings: A dict with keys/values
        :type mappings: dict
        :param time: Time in seconds that your key will expire.
        :type time: int
        :param compress_level: How much to compress.
            0 = no compression, 1 = fastest, 9 = slowest but best,
            -1 = default compression level.
        :type compress_level: int
        :return: List of keys that failed to be set on any server.
        :rtype: list
        """
        if not mappings:
            return []
        returns = set()
        server_mappings = defaultdict(dict)
        for key, value in mappings.items():
            server_key = self._get_server(key)
            server_mappings[server_key].update([(key, value)])
        for server, m in server_mappings.items():
            returns |= set(server.set_multi(m, time, compress_level))

        return list(returns)

    def add(self, key, value, time=0, compress_level=-1):
        """
        Add a key/value to server ony if it does not exist.

        :param key: Key's name
        :type key: six.string_types
        :param value: A value to be stored on server.
        :type value: object
        :param time: Time in seconds that your key will expire.
        :type time: int
        :param compress_level: How much to compress.
            0 = no compression, 1 = fastest, 9 = slowest but best,
            -1 = default compression level.
        :type compress_level: int
        :return: True if key is added False if key already exists
        :rtype: bool
        """
        server = self._get_server(key)
        return server.add(key, value, time, compress_level)

    def replace(self, key, value, time=0, compress_level=-1):
        """
        Replace a key/value to server ony if it does exist.

        :param key: Key's name
        :type key: six.string_types
        :param value: A value to be stored on server.
        :type value: object
        :param time: Time in seconds that your key will expire.
        :type time: int
        :param compress_level: How much to compress.
            0 = no compression, 1 = fastest, 9 = slowest but best,
            -1 = default compression level.
        :type compress_level: int
        :return: True if key is replace False if key does not exists
        :rtype: bool
        """
        server = self._get_server(key)
        return server.replace(key, value, time, compress_level)

    def get(self, key, default=None, get_cas=False):
        """
        Get a key from server.

        :param key: Key's name
        :type key: six.string_types
        :param default: In case memcached does not find a key, return a default value
        :param get_cas: If true, return (value, cas), where cas is the new CAS value.
        :type get_cas: boolean
        :return: Returns a key data from server.
        :rtype: object
        """
        server = self._get_server(key)
        value, cas = server.get(key)
        if value is not None:
            if get_cas:
                return value, cas
            return value

        if default is not None:
            if get_cas:
                return default, None
            return default

        if get_cas:
            return None, None

    def get_multi(self, keys, get_cas=False):
        """
        Get multiple keys from server.

        :param keys: A list of keys to from server.
        :type keys: list
        :param get_cas: If get_cas is true, each value is (data, cas), with each result's CAS value.
        :type get_cas: boolean
        :return: A dict with all requested keys.
        :rtype: dict
        """
        servers = defaultdict(list)
        d = {}
        for key in keys:
            server_key = self._get_server(key)
            servers[server_key].append(key)
        for server, keys in servers.items():
            results = server.get_multi(keys)
            if not get_cas:
                # Remove CAS data
                for key, (value, cas) in results.items():
                    results[key] = value
            d.update(results)
        return d

    def gets(self, key):
        server = self._get_server(key)
        return server.get(key)

    def cas(self, key, value, cas, time=0, compress_level=-1):
        """
        Set a value for a key on server if its CAS value matches cas.

        :param key: Key's name
        :type key: six.string_types
        :param value: A value to be stored on server.
        :type value: object
        :param cas: The CAS value previously obtained from a call to get*.
        :type cas: int
        :param time: Time in seconds that your key will expire.
        :type time: int
        :param compress_level: How much to compress.
            0 = no compression, 1 = fastest, 9 = slowest but best,
            -1 = default compression level.
        :type compress_level: int
        :return: True in case of success and False in case of failure
        :rtype: bool
        """
        server = self._get_server(key)
        return server.cas(key, value, cas, time, compress_level)

    def incr(self, key, value, default=0, time=1000000):
        """
        Increment a key, if it exists, returns it's actual value, if it don't, return 0.

        :param key: Key's name
        :type key: six.string_types
        :param value: Number to be incremented
        :type value: int
        :param default: If key not set, initialize to this value
        :type default: int
        :param time: Time in seconds that your key will expire.
        :type time: int
        :return: Actual value of the key on server
        :rtype: int
        """
        server = self._get_server(key)
        return server.incr(key, value, default=default, time=time)

    def decr(self, key, value, default=0, time=1000000):
        """
        Decrement a key, if it exists, returns it's actual value, if it don't, return 0.
        Minimum value of decrement return is 0.

        :param key: Key's name
        :type key: six.string_types
        :param value: Number to be decremented
        :type value: int
        :param default: If key not set, initialize to this value
        :type default: int
        :param time: Time in seconds that your key will expire.
        :type time: int
        :return: Actual value of the key on server
        :rtype: int
        """
        server = self._get_server(key)
        return server.decr(key, value, default=default, time=time)
