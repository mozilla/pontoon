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

import sys
import warnings

try:
    from functools import cache as _cache_package_versions
except ImportError:
    from functools import wraps
    from threading import Lock

    _package_version_cache = {}
    _package_version_cache_lock = Lock()

    def _cache_package_versions(wrapped):
        """
        Threadsafe implementation of caching for _get_package_version.

        Python 2.7 does not have the @functools.cache decorator, and
        must be reimplemented with support for clearing the cache.
        """

        @wraps(wrapped)
        def _wrapper(name):
            if name in _package_version_cache:
                return _package_version_cache[name]

            with _package_version_cache_lock:
                if name in _package_version_cache:
                    return _package_version_cache[name]

                version = _package_version_cache[name] = wrapped(name)
                return version

        def cache_clear():
            """Cache clear function to mimic @functools.cache"""
            with _package_version_cache_lock:
                _package_version_cache.clear()

        _wrapper.cache_clear = cache_clear
        return _wrapper


# Need to account for 4 possible variations of version declaration specified in (rejected) PEP 396
VERSION_ATTRS = ("__version__", "version", "__version_tuple__", "version_tuple")  # nosec
NULL_VERSIONS = frozenset((None, "", "0", "0.0", "0.0.0", "0.0.0.0", (0,), (0, 0), (0, 0, 0), (0, 0, 0, 0)))  # nosec


def get_package_version(name):
    """Gets the version string of the library.
    :param name: The name of library.
    :type name: str
    :return: The version of the library. Returns None if can't determine version.
    :type return: str or None

    Usage::
        >>> get_package_version("botocore")
                "1.1.0"
    """

    version = _get_package_version(name)

    # Coerce iterables into a string
    if isinstance(version, tuple):
        version = ".".join(str(v) for v in version)

    return version


def get_package_version_tuple(name):
    """Gets the version tuple of the library.
    :param name: The name of library.
    :type name: str
    :return: The version of the library. Returns None if can't determine version.
    :type return: tuple or None

    Usage::
        >>> get_package_version_tuple("botocore")
                (1, 1, 0)
    """

    def int_or_str(value):
        try:
            return int(value)
        except Exception:
            return str(value)

    version = _get_package_version(name)

    # Split "." separated strings and cast fields to ints
    if isinstance(version, str):
        version = tuple(int_or_str(v) for v in version.split("."))

    return version


@_cache_package_versions
def _get_package_version(name):
    module = sys.modules.get(name, None)
    version = None

    with warnings.catch_warnings(record=True):
        for attr in VERSION_ATTRS:
            try:
                version = getattr(module, attr, None)

                # In certain cases like importlib_metadata.version, version is a callable
                # function.
                if callable(version):
                    continue

                # Cast any version specified as a list into a tuple.
                version = tuple(version) if isinstance(version, list) else version
                if version not in NULL_VERSIONS:
                    return version
            except Exception:
                pass

    # importlib was introduced into the standard library starting in Python3.8.
    if "importlib" in sys.modules and hasattr(sys.modules["importlib"], "metadata"):
        try:
            # In Python3.10+ packages_distribution can be checked for as well
            if hasattr(sys.modules["importlib"].metadata, "packages_distributions"):  # pylint: disable=E1101
                distributions = sys.modules["importlib"].metadata.packages_distributions()  # pylint: disable=E1101
                distribution_name = distributions.get(name, name)
                distribution_name = distribution_name[0] if isinstance(distribution_name, list) else distribution_name
            else:
                distribution_name = name

            version = sys.modules["importlib"].metadata.version(distribution_name)  # pylint: disable=E1101
            if version not in NULL_VERSIONS:
                return version
        except Exception:
            pass

    if "pkg_resources" in sys.modules:
        try:
            version = sys.modules["pkg_resources"].get_distribution(name).version
            if version not in NULL_VERSIONS:
                return version
        except Exception:
            pass
