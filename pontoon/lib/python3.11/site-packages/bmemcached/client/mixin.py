import six

from bmemcached.client.constants import PICKLE_PROTOCOL, SOCKET_TIMEOUT
from bmemcached.compat import pickle
from bmemcached.protocol import Protocol


class ClientMixin(object):
    """ Client mixin with basic commands.

    :param servers: A list of servers with ip[:port] or unix socket.
    :type servers: list
    :param username: If your server requires SASL authentication, provide the username.
    :type username: six.string_types
    :param password: If your server requires SASL authentication, provide the password.
    :type password: six.string_types
    :param compression: This memcached client uses zlib compression by default,
        but you can change it to any Python module that provides
        `compress` and `decompress` functions, such as `bz2`.
    :type compression: Python module
    :param socket_timeout: The timeout applied to memcached connections.
    :type socket_timeout: float
    :param pickle_protocol: The pickling protocol to use, 0-5. See
        https://docs.python.org/3/library/pickle.html#data-stream-format
        default is 0 (human-readable, original format).
    :type pickle_protocol: int
    :param pickler: Use this to replace the object serialization mechanism.
    :type pickler: function
    :param unpickler: Use this to replace the object deserialization mechanism.
    :type unpickler: function
    :param tls_context: A TLS context in order to connect to TLS enabled
        memcached servers.
    :type tls_context: ssl.SSLContext
    """
    def __init__(self, servers=('127.0.0.1:11211',),
                 username=None,
                 password=None,
                 compression=None,
                 socket_timeout=SOCKET_TIMEOUT,
                 pickle_protocol=PICKLE_PROTOCOL,
                 pickler=pickle.Pickler,
                 unpickler=pickle.Unpickler,
                 tls_context=None):
        self.username = username
        self.password = password
        self.compression = compression
        self.socket_timeout = socket_timeout
        self.pickle_protocol = pickle_protocol
        self.pickler = pickler
        self.unpickler = unpickler
        self.tls_context = tls_context
        self.set_servers(servers)

    @property
    def servers(self):
        for server in self._servers:
            yield server

    def set_servers(self, servers):
        """
        Iter to a list of servers and instantiate Protocol class.

        :param servers: A list of servers
        :type servers: list
        :return: Returns nothing
        :rtype: None
        """
        if isinstance(servers, six.string_types):
            servers = [servers]

        assert servers, "No memcached servers supplied"
        self._servers = [Protocol(
            server=server,
            username=self.username,
            password=self.password,
            compression=self.compression,
            socket_timeout=self.socket_timeout,
            pickle_protocol=self.pickle_protocol,
            pickler=self.pickler,
            unpickler=self.unpickler,
            tls_context=self.tls_context,
        ) for server in servers]

    def flush_all(self, time=0):
        """
        Send a command to server flush|delete all keys.

        :param time: Time to wait until flush in seconds.
        :type time: int
        :return: True in case of success, False in case of failure
        :rtype: bool
        """
        returns = []
        for server in self.servers:
            returns.append(server.flush_all(time))

        return any(returns)

    def stats(self, key=None):
        """
        Return server stats.

        :param key: Optional if you want status from a key.
        :type key: six.string_types
        :return: A dict with server stats
        :rtype: dict
        """
        # TODO: Stats with key is not working.

        returns = {}
        for server in self.servers:
            returns[server.server] = server.stats(key)

        return returns

    def disconnect_all(self):
        """
        Disconnect all servers.

        :return: Nothing
        :rtype: None
        """
        for server in self.servers:
            server.disconnect()

    def get(self, key, default=None, get_cas=False):
        raise NotImplementedError()

    def gets(self, key):
        raise NotImplementedError()

    def get_multi(self, keys, get_cas=False):
        raise NotImplementedError()

    def set(self, key, value, time=0, compress_level=-1):
        raise NotImplementedError()

    def cas(self, key, value, cas, time=0, compress_level=-1):
        raise NotImplementedError()

    def set_multi(self, mappings, time=0, compress_level=-1):
        raise NotImplementedError()

    def add(self, key, value, time=0, compress_level=-1):
        raise NotImplementedError()

    def replace(self, key, value, time=0, compress_level=-1):
        raise NotImplementedError()

    def delete(self, key, cas=0):  # type: (six.string_types, int) -> bool
        raise NotImplementedError()

    def delete_multi(self, keys):
        raise NotImplementedError()

    def incr(self, key, value):
        # TODO: Implement missing parameters
        raise NotImplementedError()

    def decr(self, key, value):
        # TODO: Implement missing parameters
        raise NotImplementedError()
