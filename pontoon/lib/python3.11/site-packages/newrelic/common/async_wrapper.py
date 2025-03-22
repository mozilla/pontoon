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

import textwrap
import functools
from newrelic.common.coroutine import (
    is_coroutine_callable,
    is_asyncio_coroutine,
    is_generator_function,
    is_async_generator_function,
)
from newrelic.packages import six


def evaluate_wrapper(wrapper_string, wrapped, trace):
    values = {'wrapper': None, 'wrapped': wrapped,
            'trace': trace, 'functools': functools}
    exec(wrapper_string, values)
    return values['wrapper']


def coroutine_wrapper(wrapped, trace):
    WRAPPER = textwrap.dedent("""
    @functools.wraps(wrapped)
    async def wrapper(*args, **kwargs):
        with trace:
            return await wrapped(*args, **kwargs)
    """)

    try:
        return evaluate_wrapper(WRAPPER, wrapped, trace)
    except Exception:
        return wrapped


def awaitable_generator_wrapper(wrapped, trace):
    WRAPPER = textwrap.dedent("""
    import asyncio

    @functools.wraps(wrapped)
    @asyncio.coroutine
    def wrapper(*args, **kwargs):
        with trace:
            result = yield from wrapped(*args, **kwargs)
            return result
    """)

    try:
        return evaluate_wrapper(WRAPPER, wrapped, trace)
    except:
        return wrapped


if six.PY3:
    def generator_wrapper(wrapped, trace):
        WRAPPER = textwrap.dedent("""
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            with trace:
                result = yield from wrapped(*args, **kwargs)
                return result
        """)

        try:
            return evaluate_wrapper(WRAPPER, wrapped, trace)
        except:
            return wrapped
else:
    def generator_wrapper(wrapped, trace):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            g = wrapped(*args, **kwargs)
            with trace:
                try:
                    yielded = g.send(None)
                    while True:
                        try:
                            sent = yield yielded
                        except GeneratorExit as e:
                            g.close()
                            raise
                        except BaseException as e:
                            yielded = g.throw(e)
                        else:
                            yielded = g.send(sent)
                except StopIteration:
                    return
        return wrapper


def async_generator_wrapper(wrapped, trace):
    WRAPPER = textwrap.dedent("""
    @functools.wraps(wrapped)
    async def wrapper(*args, **kwargs):
        g = wrapped(*args, **kwargs)
        with trace:
            try:
                yielded = await g.asend(None)
                while True:
                    try:
                        sent = yield yielded
                    except GeneratorExit as e:
                        await g.aclose()
                        raise
                    except BaseException as e:
                        yielded = await g.athrow(e)
                    else:
                        yielded = await g.asend(sent)
            except StopAsyncIteration:
                return
    """)

    try:
        return evaluate_wrapper(WRAPPER, wrapped, trace)
    except:
        return wrapped


def async_wrapper(wrapped):
    if is_coroutine_callable(wrapped):
        return coroutine_wrapper
    elif is_async_generator_function(wrapped):
        return async_generator_wrapper
    elif is_generator_function(wrapped):
        if is_asyncio_coroutine(wrapped):
            return awaitable_generator_wrapper
        else:
            return generator_wrapper
