from bmemcached.client.constants import SOCKET_TIMEOUT

from .replicating import ReplicatingClient
from .distributed import DistributedClient

__all__ = ('Client', 'ReplicatingClient', 'DistributedClient', )


# Keep compatibility with old versions
Client = ReplicatingClient
_SOCKET_TIMEOUT = SOCKET_TIMEOUT
