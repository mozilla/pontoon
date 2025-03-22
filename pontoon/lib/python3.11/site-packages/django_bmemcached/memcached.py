import os

import bmemcached
from django.core.cache.backends import memcached
from django.core.exceptions import ImproperlyConfigured

# keys that are acceptable in the Django
# settings.CACHES[...]["OPTIONS"] dictionary.
VALID_CACHE_OPTIONS = {
    "username",
    "password",
    "compression",
    "socket_timeout",
    "pickler",
    "unpickler",
    "pickle_protocol",
}


class InvalidCacheOptions(ImproperlyConfigured):
    """Custom error raised when Client initialisation fails."""

    def __init__(self, options):
        # in Python 3 you can compare a list and set, but in Python 2
        # you cannot, so need to cast the options.keys() explicitly to a set.
        # TODO: remove set() once Python 2 support is dropped.
        invalid_options = set(options.keys()) - VALID_CACHE_OPTIONS
        msg = (
            "Error initialising BMemcached - invalid options detected: %s\n"
            "Please check your CACHES config contains only valid OPTIONS: %s"
            % (invalid_options, VALID_CACHE_OPTIONS)
        )
        super(InvalidCacheOptions, self).__init__(msg)


class BMemcached(memcached.BaseMemcachedCache):
    """
    An implementation of a cache binding using python-binary-memcached
    A.K.A BMemcached.
    """
    def __init__(self, server, params):
        params.setdefault('OPTIONS', {})

        username = params['OPTIONS'].get('username', params.get('USERNAME', os.environ.get('MEMCACHE_USERNAME')))

        if username:
            params['OPTIONS']['username'] = username

        password = params['OPTIONS'].get('password', params.get('PASSWORD', os.environ.get('MEMCACHE_PASSWORD')))

        if password:
            params['OPTIONS']['password'] = password

        if not server:
            server = tuple(os.environ.get('MEMCACHE_SERVERS', '').split(','))

        super(BMemcached, self).__init__(server, params, library=bmemcached, value_not_found_exception=ValueError)

    def close(self, **kwargs):
        # Override base behavior of disconnecting from memcache on every HTTP request.
        # This method is, in practice, only called by Django on the request_finished signal
        pass

    @property
    def _cache(self):
        client = getattr(self, '_client', None)
        if client:
            return client

        if self._options:
            try:
                client = self._lib.Client(self._servers, **self._options)
            except TypeError:
                raise InvalidCacheOptions(self._options)
        else:
            client = self._lib.Client(self._servers)

        self._client = client

        return client
