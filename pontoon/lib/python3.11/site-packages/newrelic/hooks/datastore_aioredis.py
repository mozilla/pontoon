# Copyright 2010 New Relic, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from newrelic.api.datastore_trace import DatastoreTrace
from newrelic.api.time_trace import current_trace
from newrelic.api.transaction import current_transaction
from newrelic.common.object_wrapper import function_wrapper, wrap_function_wrapper
from newrelic.common.package_version_utils import get_package_version_tuple
from newrelic.hooks.datastore_redis import (
    _redis_client_methods,
    _redis_multipart_commands,
    _redis_operation_re,
)

AIOREDIS_VERSION = get_package_version_tuple("aioredis")


def _conn_attrs_to_dict(connection):
    host = getattr(connection, "host", None)
    port = getattr(connection, "port", None)
    if not host and not port and hasattr(connection, "_address"):
        host, port = connection._address
    return {
        "host": host,
        "port": port,
        "path": getattr(connection, "path", None),
        "db": getattr(connection, "db", getattr(connection, "_db", None)),
    }


def _instance_info(kwargs):
    host = kwargs.get("host") or "localhost"
    port_path_or_id = str(kwargs.get("path") or kwargs.get("port", 6379))
    db = str(kwargs.get("db") or 0)

    return (host, port_path_or_id, db)


def _wrap_AioRedis_method_wrapper(module, instance_class_name, operation):
    @function_wrapper
    async def _nr_wrapper_AioRedis_async_method_(wrapped, instance, args, kwargs):
        transaction = current_transaction()
        if transaction is None:
            return await wrapped(*args, **kwargs)

        with DatastoreTrace(product="Redis", target=None, operation=operation):
            return await wrapped(*args, **kwargs)

    def _nr_wrapper_AioRedis_method_(wrapped, instance, args, kwargs):
        # Check for transaction and return early if found.
        # Method will return synchronously without executing,
        # it will be added to the command stack and run later.

        # This conditional is for versions of aioredis that are outside
        # New Relic's supportability window but will still work.  New
        # Relic does not provide testing/support for this.  In order to
        # keep functionality without affecting coverage metrics, this
        # segment is excluded from coverage analysis.
        if AIOREDIS_VERSION and AIOREDIS_VERSION < (2,):  # pragma: no cover
            # AioRedis v1 uses a RedisBuffer instead of a real connection for queueing up pipeline commands
            from aioredis.commands.transaction import _RedisBuffer

            if isinstance(instance._pool_or_conn, _RedisBuffer):
                # Method will return synchronously without executing,
                # it will be added to the command stack and run later.
                return wrapped(*args, **kwargs)
        else:
            # AioRedis v2 uses a Pipeline object for a client and internally queues up pipeline commands
            if AIOREDIS_VERSION:
                from aioredis.client import Pipeline
            if isinstance(instance, Pipeline):
                return wrapped(*args, **kwargs)

        # Method should be run when awaited, therefore we wrap in an async wrapper.
        return _nr_wrapper_AioRedis_async_method_(wrapped)(*args, **kwargs)

    name = "%s.%s" % (instance_class_name, operation)
    wrap_function_wrapper(module, name, _nr_wrapper_AioRedis_method_)


async def wrap_Connection_send_command(wrapped, instance, args, kwargs):
    transaction = current_transaction()
    if not transaction:
        return await wrapped(*args, **kwargs)

    host, port_path_or_id, db = (None, None, None)

    try:
        dt = transaction.settings.datastore_tracer
        if dt.instance_reporting.enabled or dt.database_name_reporting.enabled:
            conn_kwargs = _conn_attrs_to_dict(instance)
            host, port_path_or_id, db = _instance_info(conn_kwargs)
    except Exception:
        pass

    # Older Redis clients would when sending multi part commands pass
    # them in as separate arguments to send_command(). Need to therefore
    # detect those and grab the next argument from the set of arguments.

    operation = args[0].strip().lower()

    # If it's not a multi part command, there's no need to trace it, so
    # we can return early.

    if (
        operation.split()[0] not in _redis_multipart_commands
    ):  # Set the datastore info on the DatastoreTrace containing this function call.
        trace = current_trace()

        # Find DatastoreTrace no matter how many other traces are inbetween
        while trace is not None and not isinstance(trace, DatastoreTrace):
            trace = getattr(trace, "parent", None)

        if trace is not None:
            trace.host = host
            trace.port_path_or_id = port_path_or_id
            trace.database_name = db

        return await wrapped(*args, **kwargs)

    # Convert multi args to single arg string

    if operation in _redis_multipart_commands and len(args) > 1:
        operation = "%s %s" % (operation, args[1].strip().lower())

    operation = _redis_operation_re.sub("_", operation)

    with DatastoreTrace(
        product="Redis", target=None, operation=operation, host=host, port_path_or_id=port_path_or_id, database_name=db
    ):
        return await wrapped(*args, **kwargs)


# This wrapper is for versions of aioredis that are outside
# New Relic's supportability window but will still work.  New
# Relic does not provide testing/support for this.  In order to
# keep functionality without affecting coverage metrics, this
# segment is excluded from coverage analysis.
def wrap_RedisConnection_execute(wrapped, instance, args, kwargs):  # pragma: no cover
    # RedisConnection in aioredis v1 returns a future instead of using coroutines
    transaction = current_transaction()
    if not transaction:
        return wrapped(*args, **kwargs)

    host, port_path_or_id, db = (None, None, None)

    try:
        dt = transaction.settings.datastore_tracer
        if dt.instance_reporting.enabled or dt.database_name_reporting.enabled:
            conn_kwargs = _conn_attrs_to_dict(instance)
            host, port_path_or_id, db = _instance_info(conn_kwargs)
    except Exception:
        pass

    # Older Redis clients would when sending multi part commands pass
    # them in as separate arguments to send_command(). Need to therefore
    # detect those and grab the next argument from the set of arguments.

    operation = args[0].strip().lower()

    # If it's not a multi part command, there's no need to trace it, so
    # we can return early.

    if (
        operation.split()[0] not in _redis_multipart_commands
    ):  # Set the datastore info on the DatastoreTrace containing this function call.
        trace = current_trace()

        # Find DatastoreTrace no matter how many other traces are inbetween
        while trace is not None and not isinstance(trace, DatastoreTrace):
            trace = getattr(trace, "parent", None)

        if trace is not None:
            trace.host = host
            trace.port_path_or_id = port_path_or_id
            trace.database_name = db

        return wrapped(*args, **kwargs)

    # Convert multi args to single arg string

    if operation in _redis_multipart_commands and len(args) > 1:
        operation = "%s %s" % (operation, args[1].strip().lower())

    operation = _redis_operation_re.sub("_", operation)

    with DatastoreTrace(
        product="Redis", target=None, operation=operation, host=host, port_path_or_id=port_path_or_id, database_name=db
    ):
        return wrapped(*args, **kwargs)


def instrument_aioredis_client(module):
    # StrictRedis is just an alias of Redis, no need to wrap it as well.
    if hasattr(module, "Redis"):
        class_ = getattr(module, "Redis")
        for operation in _redis_client_methods:
            if hasattr(class_, operation):
                _wrap_AioRedis_method_wrapper(module, "Redis", operation)


def instrument_aioredis_connection(module):
    if hasattr(module, "Connection"):
        if hasattr(module.Connection, "send_command"):
            wrap_function_wrapper(module, "Connection.send_command", wrap_Connection_send_command)

    # This conditional is for versions of aioredis that are outside
    # New Relic's supportability window but will still work.  New
    # Relic does not provide testing/support for this.  In order to
    # keep functionality without affecting coverage metrics, this
    # segment is excluded from coverage analysis.
    if hasattr(module, "RedisConnection"):  # pragma: no cover
        if hasattr(module.RedisConnection, "execute"):
            wrap_function_wrapper(module, "RedisConnection.execute", wrap_RedisConnection_execute)
