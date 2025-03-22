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
import inspect
from collections import namedtuple

from newrelic.common.object_names import object_context

_CodeLevelMetricsNode = namedtuple(
    "CodeLevelMetricsNode",
    [
        "filepath",
        "function",
        "lineno",
        "namespace",
    ],
)


class CodeLevelMetricsNode(_CodeLevelMetricsNode):
    def add_attrs(self, add_attr_function):
        # Add attributes
        for k, v in self._asdict().items():
            if v is not None:
                add_attr_function("code.%s" % k, v)


def extract_code_from_callable(func):
    """Extract source code context from a callable and add appropriate attributes."""
    original_func = func  # Save original reference

    if hasattr(func, "_nr_source_code"):
        return func._nr_source_code

    # Fully unwrap object
    while (hasattr(func, "__wrapped__") and func.__wrapped__ is not None) or isinstance(func, functools.partial):
        # Remove Partials
        if isinstance(func, functools.partial):
            func = func.func
        # Unwrap wrapped objects
        else:
            if func.__wrapped__ == func:
                # Infinite loop protection
                break

            func = func.__wrapped__

    # Retrieve basic object details
    module_name, func_path = object_context(func)

    if inspect.isbuiltin(func):
        # Set attributes for builtins
        file_path = "<builtin>"
        line_number = None
    elif hasattr(func, "__code__"):
        # Extract details from function __code__ attr
        co = func.__code__
        line_number = co.co_firstlineno
        file_path = co.co_filename
    else:
        # Extract call method for callable objects
        if inspect.isclass(func):
            # For class types don't change anything
            pass
        elif hasattr(func, "__call__"):
            # For callable object, use the __call__ attribute
            func = func.__call__
            module_name, func_path = object_context(func)
        elif hasattr(func, "__class__"):
            # Extract class from object instances
            func = func.__class__

        # Initialize here instead of in except to potentially get file_path but not line_number
        file_path = None
        line_number = None
        try:
            # Use inspect to get file and line number
            file_path = inspect.getsourcefile(func)
            line_number = inspect.getsourcelines(func)[1]
        except Exception:
            pass

    # Split function path to extract class name
    func_path = func_path.split(".")
    func_name = func_path[-1]  # function name is last in path
    if len(func_path) > 1:
        class_name = ".".join((func_path[:-1]))
        namespace = ".".join((module_name, class_name))
    else:
        namespace = module_name

    node = CodeLevelMetricsNode(
        filepath=file_path,
        function=func_name,
        lineno=line_number,
        namespace=namespace,
    )

    try:
        if hasattr(original_func, "__func__"):
            # Must store on underlying function not bound method
            original_func = original_func.__func__
        original_func._nr_source_code = node
    except Exception:  # Don't raise exceptions for any reason
        pass

    return node


def extract_code_from_traceback(tb):
    # Walk traceback
    while getattr(tb, "tb_next", None) is not None:
        tb = tb.tb_next

    frame = tb.tb_frame
    code = frame.f_code

    # Extract exception source code
    lineno = tb.tb_lineno
    filepath = code.co_filename
    funcname = code.co_name

    return CodeLevelMetricsNode(filepath=filepath, lineno=lineno, function=funcname, namespace=None)
