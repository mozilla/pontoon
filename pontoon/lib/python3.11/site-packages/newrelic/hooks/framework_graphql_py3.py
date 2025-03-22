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
import functools
import sys

from newrelic.api.error_trace import ErrorTrace
from newrelic.api.function_trace import FunctionTrace


def nr_coro_execute_name_wrapper(wrapped, result, set_name):
    @functools.wraps(wrapped)
    async def _nr_coro_execute_name_wrapper():
        result_ = await result
        set_name()
        return result_

    return _nr_coro_execute_name_wrapper()


def nr_coro_resolver_error_wrapper(wrapped, name, trace, ignore, result, transaction):
    @functools.wraps(wrapped)
    async def _nr_coro_resolver_error_wrapper():
        with trace:
            with ErrorTrace(ignore=ignore):
                try:
                    return await result
                except Exception:
                    transaction.set_transaction_name(name, "GraphQL", priority=15)
                    raise

    return _nr_coro_resolver_error_wrapper()


def nr_coro_resolver_wrapper(wrapped, trace, ignore, result):
    @functools.wraps(wrapped)
    async def _nr_coro_resolver_wrapper():
        with trace:
            with ErrorTrace(ignore=ignore):
                return await result

    return _nr_coro_resolver_wrapper()

def nr_coro_graphql_impl_wrapper(wrapped, trace, ignore, result):
    @functools.wraps(wrapped)
    async def _nr_coro_graphql_impl_wrapper():
        try:
            with ErrorTrace(ignore=ignore):
                result_ = await result
        except:
            trace.__exit__(*sys.exc_info())
            raise
        else:
            trace.__exit__(None, None, None)
            return result_


    return _nr_coro_graphql_impl_wrapper()