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

from newrelic.api.asgi_application import wrap_asgi_application
from newrelic.api.error_trace import ErrorTrace
from newrelic.api.graphql_trace import GraphQLOperationTrace
from newrelic.api.transaction import current_transaction
from newrelic.common.object_names import callable_name
from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.common.package_version_utils import get_package_version
from newrelic.core.graphql_utils import graphql_statement
from newrelic.hooks.framework_graphql import GRAPHQL_VERSION, ignore_graphql_duplicate_exception

STRAWBERRY_GRAPHQL_VERSION = get_package_version("strawberry-graphql")
strawberry_version_tuple = tuple(map(int, STRAWBERRY_GRAPHQL_VERSION.split(".")))


def bind_execute(query, *args, **kwargs):
    return query


def wrap_execute_sync(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if not transaction:
        return wrapped(*args, **kwargs)

    try:
        query = bind_execute(*args, **kwargs)
    except TypeError:
        return wrapped(*args, **kwargs)

    transaction.add_framework_info(name="Strawberry", version=STRAWBERRY_GRAPHQL_VERSION)
    transaction.add_framework_info(name="GraphQL", version=GRAPHQL_VERSION)

    if hasattr(query, "body"):
        query = query.body

    transaction.set_transaction_name(callable_name(wrapped), "GraphQL", priority=10)

    with GraphQLOperationTrace(source=wrapped) as trace:
        trace.product = "Strawberry"
        trace.statement = graphql_statement(query)
        with ErrorTrace(ignore=ignore_graphql_duplicate_exception):
            return wrapped(*args, **kwargs)


async def wrap_execute(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if not transaction:
        return await wrapped(*args, **kwargs)

    try:
        query = bind_execute(*args, **kwargs)
    except TypeError:
        return await wrapped(*args, **kwargs)

    transaction.add_framework_info(name="Strawberry", version=STRAWBERRY_GRAPHQL_VERSION)
    transaction.add_framework_info(name="GraphQL", version=GRAPHQL_VERSION)

    if hasattr(query, "body"):
        query = query.body

    transaction.set_transaction_name(callable_name(wrapped), "GraphQL", priority=10)

    with GraphQLOperationTrace(source=wrapped) as trace:
        trace.product = "Strawberry"
        trace.statement = graphql_statement(query)
        with ErrorTrace(ignore=ignore_graphql_duplicate_exception):
            return await wrapped(*args, **kwargs)


def bind_from_resolver(field, *args, **kwargs):
    return field


def wrap_from_resolver(wrapped, instance, args, kwargs):
    result = wrapped(*args, **kwargs)

    try:
        field = bind_from_resolver(*args, **kwargs)
    except TypeError:
        pass
    else:
        if hasattr(field, "base_resolver"):
            if hasattr(field.base_resolver, "wrapped_func"):
                result._nr_base_resolver = field.base_resolver.wrapped_func

    return result


def instrument_strawberry_schema(module):
    if strawberry_version_tuple < (0, 23, 3):
        return
    if hasattr(module, "Schema"):
        if hasattr(module.Schema, "execute"):
            wrap_function_wrapper(module, "Schema.execute", wrap_execute)
        if hasattr(module.Schema, "execute_sync"):
            wrap_function_wrapper(module, "Schema.execute_sync", wrap_execute_sync)


def instrument_strawberry_asgi(module):
    if strawberry_version_tuple < (0, 23, 3):
        return
    if hasattr(module, "GraphQL"):
        wrap_asgi_application(module, "GraphQL.__call__", framework=("Strawberry", STRAWBERRY_GRAPHQL_VERSION))


def instrument_strawberry_schema_converter(module):
    if strawberry_version_tuple < (0, 23, 3):
        return
    if hasattr(module, "GraphQLCoreConverter"):
        if hasattr(module.GraphQLCoreConverter, "from_resolver"):
            wrap_function_wrapper(module, "GraphQLCoreConverter.from_resolver", wrap_from_resolver)
