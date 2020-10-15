import errno
import os
import scandir

from pontoon.base.models import Resource
from pontoon.base.utils import extension_in, first


def is_hidden(path):
    """
    Return true if path contains hidden directory.
    """
    for p in path.split(os.sep):
        if p.startswith("."):
            return True
    return False


def is_resource(filename):
    """
    Return True if the filename's extension is a supported Resource
    format.
    """
    return extension_in(filename, Resource.ALLOWED_EXTENSIONS)


def is_source_resource(filename):
    """
    Return True if the filename's extension is a source-only Resource
    format.
    """
    return extension_in(filename, Resource.SOURCE_EXTENSIONS)


def is_asymmetric_resource(filename):
    """
    Return True if the filename's extension is an asymmetric Resource
    format.
    """
    return extension_in(filename, Resource.ASYMMETRIC_FORMATS)


def get_parent_directory(path):
    """
    Get parent directory of the path
    """
    return os.path.abspath(os.path.join(path, os.pardir))


def uses_undercore_as_separator(directory):
    """
    Return True if any subdirectory contains underscore.
    """
    subdirs = os.listdir(directory)
    return "".join(subdirs).count("_") > "".join(subdirs).count("-")


def directory_contains_resources(directory_path, source_only=False):
    """
    Return True if the given directory contains at least one
    supported resource file (checked via file extension), or False
    otherwise.

    :param source_only:
        If True, only check for source-only formats.
    """
    resource_check = is_source_resource if source_only else is_resource
    for root, dirnames, filenames in scandir.walk(directory_path):
        # first() avoids checking past the first matching resource.
        if first(filenames, resource_check) is not None:
            return True
    return False


def locale_directory_path(checkout_path, locale_code, parent_directories=None):
    """
    Path to the directory where strings for the given locale are
    stored.
    """
    possible_paths = []

    # Check paths that use underscore as locale/country code separator
    locale_code_variants = [locale_code, locale_code.replace("-", "_")]

    # Optimization for directories with a lot of paths: if parent_directories
    # is provided, we simply join it with locale_code and check if path exists
    for parent_directory in parent_directories:
        for locale in locale_code_variants:
            candidate = os.path.join(parent_directory, locale)
            if os.path.exists(candidate):
                possible_paths.append(candidate)

    if not possible_paths:
        for root, dirnames, filenames in scandir.walk(checkout_path):
            for locale in locale_code_variants:
                if locale in dirnames:
                    possible_paths.append(os.path.join(root, locale))

    for possible_path in possible_paths:
        if directory_contains_resources(possible_path):
            return possible_path

    # If locale directory empty (asymmetric formats)
    if possible_paths:
        return possible_paths[0]

    raise IOError(
        "Directory for locale `{0}` not found".format(locale_code or "source")
    )


def locale_to_source_path(path):
    """
    Return source resource path for the given locale resource path.
    Source files for .po files are actually .pot.
    """
    if path.endswith("po"):
        path += "t"
    return path


def source_to_locale_path(path):
    """
    Return locale resource path for the given source resource path.
    Locale files for .pot files are actually .po.
    """
    if path.endswith("pot"):
        path = path[:-1]
    return path


def escape_quotes(value):
    """
    DTD files can use single or double quotes for identifying strings,
    so &quot; and &apos; are the safe bet that will work in both cases.
    """
    value = value.replace('"', "\\&quot;")
    value = value.replace("'", "\\&apos;")

    return value


def unescape_quotes(value):
    value = value.replace("\\&quot;", '"')
    value = value.replace("\\u0022", '"')  # Bug 1390111
    value = value.replace('\\"', '"')

    value = value.replace("\\&apos;", "'")
    value = value.replace("\\u0027", "'")  # Bug 1390111
    value = value.replace("\\'", "'")

    return value


def create_parent_directory(path):
    """
    Create parent directory of the given path if it doesn't exist yet.
    """
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as e:
        # Directory already exists
        if e.errno == errno.EEXIST:
            pass
        else:
            raise
