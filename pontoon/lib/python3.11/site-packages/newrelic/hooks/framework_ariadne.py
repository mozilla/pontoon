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

from inspect import isawaitable

from newrelic.api.asgi_application import wrap_asgi_application
from newrelic.api.error_trace import ErrorTrace
from newrelic.api.graphql_trace import GraphQLOperationTrace
from newrelic.api.transaction import current_transaction
from newrelic.api.wsgi_application import wrap_wsgi_application
from newrelic.common.object_names import callable_name
from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.common.package_version_utils import get_package_version
from newrelic.core.graphql_utils import graphql_statement
from newrelic.hooks.framework_graphql import GRAPHQL_VERSION, ignore_graphql_duplicate_exception

ARIADNE_VERSION = get_package_version("ariadne")
ariadne_version_tuple = tuple(map(int, ARIADNE_VERSION.split(".")))


def bind_graphql(schema, data, *args, **kwargs):
    return data


def wrap_graphql_sync(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if not transaction:
        return wrapped(*args, **kwargs)

    try:
        data = bind_graphql(*args, **kwargs)
    except TypeError:
        return wrapped(*args, **kwargs)

    transaction.add_framework_info(name="Ariadne", version=ARIADNE_VERSION)
    transaction.add_framework_info(name="GraphQL", version=GRAPHQL_VERSION)

    query = data["query"]
    if hasattr(query, "body"):
        query = query.body

    transaction.set_transaction_name(callable_name(wrapped), "GraphQL", priority=10)

    with GraphQLOperationTrace(source=wrapped) as trace:
        trace.product = "Ariadne"
        trace.statement = graphql_statement(query)
        with ErrorTrace(ignore=ignore_graphql_duplicate_exception):
            return wrapped(*args, **kwargs)


async def wrap_graphql(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if not transaction:
        result = wrapped(*args, **kwargs)
        if isawaitable(result):
            result = await result
        return result

    try:
        data = bind_graphql(*args, **kwargs)
    except TypeError:
        result = wrapped(*args, **kwargs)
        if isawaitable(result):
            result = await result
        return result

    transaction.add_framework_info(name="Ariadne", version=ARIADNE_VERSION)
    transaction.add_framework_info(name="GraphQL", version=GRAPHQL_VERSION)

    query = data["query"]
    if hasattr(query, "body"):
        query = query.body

    transaction.set_transaction_name(callable_name(wrapped), "GraphQL", priority=10)

    with GraphQLOperationTrace(source=wrapped) as trace:
        trace.product = "Ariadne"
        trace.statement = graphql_statement(query)
        with ErrorTrace(ignore=ignore_graphql_duplicate_exception):
            result = wrapped(*args, **kwargs)
            if isawaitable(result):
                result = await result
            return result


def instrument_ariadne_execute(module):
    # v0.9.0 is the version where ariadne started using graphql-core v3
    if ariadne_version_tuple < (0, 9):
        return
    if hasattr(module, "graphql"):
        wrap_function_wrapper(module, "graphql", wrap_graphql)

    if hasattr(module, "graphql_sync"):
        wrap_function_wrapper(module, "graphql_sync", wrap_graphql_sync)


def instrument_ariadne_asgi(module):
    if ariadne_version_tuple < (0, 9):
        return
    if hasattr(module, "GraphQL"):
        wrap_asgi_application(module, "GraphQL.__call__", framework=("Ariadne", ARIADNE_VERSION))


def instrument_ariadne_wsgi(module):
    if ariadne_version_tuple < (0, 9):
        return
    if hasattr(module, "GraphQL"):
        wrap_wsgi_application(module, "GraphQL.__call__", framework=("Ariadne", ARIADNE_VERSION))
