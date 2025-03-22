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

from newrelic.api.asgi_application import ASGIApplicationWrapper
from newrelic.api.wsgi_application import WSGIApplicationWrapper
from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.common.package_version_utils import get_package_version


def bind_worker_serve(app, *args, **kwargs):
    return app, args, kwargs


async def wrap_worker_serve(wrapped, instance, args, kwargs):
    import hypercorn

    dispatcher_details = ("Hypercorn", get_package_version("hypercorn"))
    wrapper_module = getattr(hypercorn, "app_wrappers", None)
    asgi_wrapper_class = getattr(wrapper_module, "ASGIWrapper", None)
    wsgi_wrapper_class = getattr(wrapper_module, "WSGIWrapper", None)

    app, args, kwargs = bind_worker_serve(*args, **kwargs)

    # Hypercorn 0.14.1 introduced wrappers for ASGI and WSGI apps that need to be above our instrumentation.
    if asgi_wrapper_class is not None and isinstance(app, asgi_wrapper_class):
        app.app = ASGIApplicationWrapper(app.app, dispatcher=dispatcher_details)
    elif wsgi_wrapper_class is not None and isinstance(app, wsgi_wrapper_class):
        app.app = WSGIApplicationWrapper(app.app, dispatcher=dispatcher_details)
    else:
        app = ASGIApplicationWrapper(app, dispatcher=dispatcher_details)

    app._nr_wrapped = True

    return await wrapped(app, *args, **kwargs)


def bind_is_asgi(app):
    return app


def wrap_is_asgi(wrapped, instance, args, kwargs):
    # Wrapper is identical and reused for the functions is_asgi and _is_asgi_2.
    app = bind_is_asgi(*args, **kwargs)

    # Unwrap apps wrapped by our instrumentation.
    # ASGI 2/3 detection for hypercorn is unable to process
    # our wrappers and will return incorrect results. This
    # should be sufficient to allow hypercorn to run detection
    # on an application that was not wrapped by this instrumentation.
    while getattr(app, "_nr_wrapped", False):
        app = app.__wrapped__

    return wrapped(app)


def instrument_hypercorn_asyncio_run(module):
    if hasattr(module, "worker_serve"):
        wrap_function_wrapper(module, "worker_serve", wrap_worker_serve)


def instrument_hypercorn_trio_run(module):
    if hasattr(module, "worker_serve"):
        wrap_function_wrapper(module, "worker_serve", wrap_worker_serve)


def instrument_hypercorn_utils(module):
    if hasattr(module, "_is_asgi_2"):
        wrap_function_wrapper(module, "_is_asgi_2", wrap_is_asgi)

    if hasattr(module, "is_asgi"):
        wrap_function_wrapper(module, "is_asgi", wrap_is_asgi)
