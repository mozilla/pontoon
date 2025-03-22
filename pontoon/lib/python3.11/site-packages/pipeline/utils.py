try:
    import fcntl
except ImportError:
    # windows
    fcntl = None

import importlib
import mimetypes
import os
import posixpath
import sys
from urllib.parse import quote

from django.utils.encoding import smart_str

from pipeline.conf import settings


def to_class(class_str):
    if not class_str:
        return None

    module_bits = class_str.split(".")
    module_path, class_name = ".".join(module_bits[:-1]), module_bits[-1]
    module = importlib.import_module(module_path)
    return getattr(module, class_name, None)


def filepath_to_uri(path):
    if path is None:
        return path
    return quote(smart_str(path).replace("\\", "/"), safe="/~!*()'#?")


def guess_type(path, default=None):
    for type, ext in settings.MIMETYPES:
        mimetypes.add_type(type, ext)
    mimetype, _ = mimetypes.guess_type(path)
    if not mimetype:
        return default
    return smart_str(mimetype)


def relpath(path, start=posixpath.curdir):
    """Return a relative version of a path"""
    if not path:
        raise ValueError("no path specified")

    start_list = posixpath.abspath(start).split(posixpath.sep)
    path_list = posixpath.abspath(path).split(posixpath.sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(posixpath.commonprefix([start_list, path_list]))

    rel_list = [posixpath.pardir] * (len(start_list) - i) + path_list[i:]
    if not rel_list:
        return posixpath.curdir
    return posixpath.join(*rel_list)


def set_std_streams_blocking():
    """
    Set stdout and stderr to be blocking.

    This is called after Popen.communicate() to revert stdout and stderr back
    to be blocking (the default) in the event that the process to which they
    were passed manipulated one or both file descriptors to be non-blocking.
    """
    if not fcntl:
        return
    for f in (sys.__stdout__, sys.__stderr__):
        fileno = f.fileno()
        flags = fcntl.fcntl(fileno, fcntl.F_GETFL)
        fcntl.fcntl(fileno, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
