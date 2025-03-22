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

from newrelic.common.object_wrapper import FunctionWrapper, wrap_function_wrapper

# This is NOT a fully-featured instrumentation for the sentry SDK. Instead
# this is a monkey-patch of the sentry SDK to work around a bug that causes
# improper ASGI 2/3 version detection when inspecting our wrappers. We fix this
# by manually unwrapping the application when version detection is run.


def bind__looks_like_asgi3(app):
    return app


def wrap__looks_like_asgi3(wrapped, instance, args, kwargs):
    try:
        app = bind__looks_like_asgi3(*args, **kwargs)
    except Exception:
        return wrapped(*args, **kwargs)

    while isinstance(app, FunctionWrapper) and hasattr(app, "__wrapped__"):
        app = app.__wrapped__

    return wrapped(app)


def instrument_sentry_sdk_integrations_asgi(module):
    if hasattr(module, "_looks_like_asgi3"):
        wrap_function_wrapper(module, "_looks_like_asgi3", wrap__looks_like_asgi3)
