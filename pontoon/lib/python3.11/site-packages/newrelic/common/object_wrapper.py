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

"""This module implements a generic object wrapper for use in performing
monkey patching, helper functions to perform monkey patching and general
purpose decorators and wrapper functions for various basic tasks one can
make use of when doing monkey patching.

"""

import inspect
import warnings

from newrelic.packages.wrapt import BoundFunctionWrapper as _BoundFunctionWrapper
from newrelic.packages.wrapt import CallableObjectProxy as _CallableObjectProxy
from newrelic.packages.wrapt import FunctionWrapper as _FunctionWrapper
from newrelic.packages.wrapt import ObjectProxy as _ObjectProxy
from newrelic.packages.wrapt import (  # noqa: F401; pylint: disable=W0611
    apply_patch,
    resolve_path,
    wrap_object,
    wrap_object_attribute,
)

# We previously had our own pure Python implementation of the generic
# object wrapper but we now defer to using the wrapt module as its C
# implementation has less than ten percent of the overhead for the common
# case of instance methods. Even the wrapt pure Python implementation
# of wrapt has about fifty percent of the overhead. The wrapt module
# implementation is also much more comprehensive as far as being a
# transparent object proxy. The only problem is that until we can cut
# over completely to a generic API, we need to maintain the existing API
# we used. This requires the fiddles below where we need to customise by
# what names everything is accessed. Note that with the code below, the
# _ObjectWrapperBase class must come first in the base class list of
# the derived class to ensure correct precedence order on base class
# method lookup for __setattr__(), __getattr__() and __delattr__(). Also
# the intention eventually is that ObjectWrapper is deprecated. Either
# ObjectProxy or FunctionWrapper should be used going forward.


class ObjectProxy(_ObjectProxy):
    """
    This class provides method overrides for all object wrappers used by the
    agent. These methods allow attributes to be defined with the special prefix
    _nr_ to be interpretted as attributes on the wrapper, rather than the
    wrapped object. Inheriting from the base class wrapt.ObjectProxy preserves
    method resolution order (MRO) through multiple inheritance.
    (See https://www.python.org/download/releases/2.3/mro/).
    """

    def __setattr__(self, name, value):
        if name.startswith("_nr_"):
            name = name.replace("_nr_", "_self_", 1)
            setattr(self, name, value)
        else:
            super(ObjectProxy, self).__setattr__(name, value)

    def __getattr__(self, name):
        if name.startswith("_nr_"):
            name = name.replace("_nr_", "_self_", 1)
            return getattr(self, name)
        else:
            return super(ObjectProxy, self).__getattr__(name)

    def __delattr__(self, name):
        if name.startswith("_nr_"):
            name = name.replace("_nr_", "_self_", 1)
            delattr(self, name)
        else:
            super(ObjectProxy, self).__delattr__(name)

    @property
    def _nr_next_object(self):
        return self.__wrapped__

    @property
    def _nr_last_object(self):
        try:
            return self._self_last_object
        except AttributeError:
            self._self_last_object = getattr(self.__wrapped__, "_nr_last_object", self.__wrapped__)
            return self._self_last_object

    @property
    def _nr_instance(self):
        return self._self_instance

    @property
    def _nr_wrapper(self):
        return self._self_wrapper

    @property
    def _nr_parent(self):
        return self._self_parent


class _NRBoundFunctionWrapper(ObjectProxy, _BoundFunctionWrapper):
    pass


class FunctionWrapper(ObjectProxy, _FunctionWrapper):
    __bound_function_wrapper__ = _NRBoundFunctionWrapper


class CallableObjectProxy(ObjectProxy, _CallableObjectProxy):
    pass


# The ObjectWrapper class needs to be deprecated and removed once all our
# own code no longer uses it. It reaches down into what are wrapt internals
# at present which shouldn't be doing.

class ObjectWrapper(FunctionWrapper):
    def __init__(self, wrapped, instance, wrapper):
        warnings.warn(
            ("The ObjectWrapper API is deprecated. Please use one of ObjectProxy, FunctionWrapper, or CallableObjectProxy instead."),
            DeprecationWarning,
        )
        super(ObjectWrapper, self).__init__(wrapped, wrapper)


# Function for creating a decorator for applying to functions, as well as
# short cut functions for applying wrapper functions via monkey patching.

# WARNING: These functions are reproduced directly from wrapt, but using
# our FunctionWrapper class which includes the _nr_ attriubte overrides
# that are inherited from our subclass of wrapt.ObjectProxy.These MUST be
# kept in sync with wrapt when upgrading, or drift may introduce bugs.


def function_wrapper(wrapper):
    def _wrapper(wrapped, instance, args, kwargs):
        target_wrapped = args[0]
        if instance is None:
            target_wrapper = wrapper
        elif inspect.isclass(instance):
            target_wrapper = wrapper.__get__(None, instance)
        else:
            target_wrapper = wrapper.__get__(instance, type(instance))
        return FunctionWrapper(target_wrapped, target_wrapper)

    return FunctionWrapper(wrapper, _wrapper)


def wrap_function_wrapper(module, name, wrapper):
    return wrap_object(module, name, FunctionWrapper, (wrapper,))


def patch_function_wrapper(module, name, enabled=None):
    def _wrapper(wrapper):
        return wrap_object(module, name, FunctionWrapper, (wrapper, enabled))

    return _wrapper


def transient_function_wrapper(module, name):
    def _decorator(wrapper):
        def _wrapper(wrapped, instance, args, kwargs):
            target_wrapped = args[0]
            if instance is None:
                target_wrapper = wrapper
            elif inspect.isclass(instance):
                target_wrapper = wrapper.__get__(None, instance)
            else:
                target_wrapper = wrapper.__get__(instance, type(instance))

            def _execute(wrapped, instance, args, kwargs):
                (parent, attribute, original) = resolve_path(module, name)
                replacement = FunctionWrapper(original, target_wrapper)
                setattr(parent, attribute, replacement)
                try:
                    return wrapped(*args, **kwargs)
                finally:
                    setattr(parent, attribute, original)

            return FunctionWrapper(target_wrapped, _execute)

        return FunctionWrapper(wrapper, _wrapper)

    return _decorator


# Generic decorators for performing actions before and after a wrapped
# function is called, or modifying the inbound arguments or return value.


def pre_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        if instance is not None:
            function(instance, *args, **kwargs)
        else:
            function(*args, **kwargs)
        return wrapped(*args, **kwargs)

    return _wrapper


def PreFunctionWrapper(wrapped, function):
    return pre_function(function)(wrapped)


def wrap_pre_function(module, object_path, function):
    return wrap_object(module, object_path, PreFunctionWrapper, (function,))


def post_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        result = wrapped(*args, **kwargs)
        if instance is not None:
            function(instance, *args, **kwargs)
        else:
            function(*args, **kwargs)
        return result

    return _wrapper


def PostFunctionWrapper(wrapped, function):
    return post_function(function)(wrapped)


def wrap_post_function(module, object_path, function):
    return wrap_object(module, object_path, PostFunctionWrapper, (function,))


def in_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        if instance is not None:
            args, kwargs = function(instance, *args, **kwargs)

            # The instance is passed into the supplied function and for
            # consistency it is also expected to also be returned
            # otherwise it gets fiddly for the supplied function to
            # remove it. It is expected that the instance returned in
            # the arguments is the same value as it is simply dropped
            # after being returned. This is necessary as the instance is
            # not passed through anyway in arguments to the wrapped
            # function, as the instance is already bound to the wrapped
            # function at this point and supplied automatically.

            return wrapped(*args[1:], **kwargs)

        args, kwargs = function(*args, **kwargs)
        return wrapped(*args, **kwargs)

    return _wrapper


def InFunctionWrapper(wrapped, function):
    return in_function(function)(wrapped)


def wrap_in_function(module, object_path, function):
    return wrap_object(module, object_path, InFunctionWrapper, (function,))


def out_function(function):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        return function(wrapped(*args, **kwargs))

    return _wrapper


def OutFunctionWrapper(wrapped, function):
    return out_function(function)(wrapped)


def wrap_out_function(module, object_path, function):
    return wrap_object(module, object_path, OutFunctionWrapper, (function,))
