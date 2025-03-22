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
from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.hooks.datastore_redis import (
    _conn_attrs_to_dict,
    _instance_info,
    _redis_client_methods,
    _redis_multipart_commands,
    _redis_operation_re,
)


def _wrap_Aredis_method_wrapper_(module, instance_class_name, operation):
    async def _nr_wrapper_Aredis_method_(wrapped, instance, args, kwargs):
        transaction = current_transaction()
        if transaction is None:
            return await wrapped(*args, **kwargs)

        with DatastoreTrace(product="Redis", target=None, operation=operation):
            return await wrapped(*args, **kwargs)

    name = "%s.%s" % (instance_class_name, operation)
    wrap_function_wrapper(module, name, _nr_wrapper_Aredis_method_)


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

    if operation.split()[0] not in _redis_multipart_commands:
        # Set the datastore info on the DatastoreTrace containing this function call.
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


def instrument_aredis_client(module):
    if hasattr(module, "StrictRedis"):
        for name in _redis_client_methods:
            if hasattr(module.StrictRedis, name):
                _wrap_Aredis_method_wrapper_(module, "StrictRedis", name)


def instrument_aredis_connection(module):
    wrap_function_wrapper(module, "Connection.send_command", wrap_Connection_send_command)
