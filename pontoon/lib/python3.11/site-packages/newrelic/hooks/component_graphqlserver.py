from newrelic.api.error_trace import ErrorTrace
from newrelic.api.graphql_trace import GraphQLOperationTrace
from newrelic.api.transaction import current_transaction
from newrelic.common.object_names import callable_name
from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.common.package_version_utils import get_package_version
from newrelic.core.graphql_utils import graphql_statement
from newrelic.hooks.framework_graphql import (
    GRAPHQL_VERSION,
    ignore_graphql_duplicate_exception,
)

GRAPHQL_SERVER_VERSION = get_package_version("graphql-server")
graphql_server_major_version = int(GRAPHQL_SERVER_VERSION.split(".")[0])


def bind_query(schema, params, *args, **kwargs):
    return getattr(params, "query", None)


def wrap_get_response(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if not transaction:
        return wrapped(*args, **kwargs)

    try:
        query = bind_query(*args, **kwargs)
    except TypeError:
        return wrapped(*args, **kwargs)

    transaction.add_framework_info(name="GraphQLServer", version=GRAPHQL_SERVER_VERSION)
    transaction.add_framework_info(name="GraphQL", version=GRAPHQL_VERSION)

    if hasattr(query, "body"):
        query = query.body

    transaction.set_transaction_name(callable_name(wrapped), "GraphQL", priority=10)

    with GraphQLOperationTrace() as trace:
        trace.product = "GraphQLServer"
        trace.statement = graphql_statement(query)
        with ErrorTrace(ignore=ignore_graphql_duplicate_exception):
            return wrapped(*args, **kwargs)


def instrument_graphqlserver(module):
    if graphql_server_major_version <= 2:
        return
    wrap_function_wrapper(module, "get_response", wrap_get_response)
