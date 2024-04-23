import errno
import os

from pontoon.base.models import Resource
from pontoon.base.utils import extension_in, first


def is_hidden(path: str) -> bool:
    """
    Return true if path contains hidden directory.
    """
    for p in path.split(os.sep):
        if p.startswith("."):
            return True
    return False


def is_resource(filename: str) -> bool:
    """
    Return True if the filename's extension is a supported Resource
    format.
    """
    return extension_in(filename, Resource.ALLOWED_EXTENSIONS)


def is_source_resource(filename: str) -> bool:
    """
    Return True if the filename's extension is a source-only Resource
    format.
    """
    return extension_in(filename, Resource.SOURCE_EXTENSIONS)


def is_asymmetric_resource(filename: str) -> bool:
    """
    Return True if the filename's extension is an asymmetric Resource
    format.
    """
    return extension_in(filename, Resource.ASYMMETRIC_FORMATS)


def get_parent_directory(path: str) -> str:
    """
    Get parent directory of the path
    """
    return os.path.abspath(os.path.join(path, os.pardir))


def uses_undercore_as_separator(directory: str) -> bool:
    """
    Return True if the names of folders in a directory contain more '_' than '-'.
    """
    only_folders = []
    subdirs = os.listdir(directory)

    for i in subdirs:
        if os.path.isdir(os.path.join(directory, i)):
            only_folders.append(i)

    return "".join(only_folders).count("_") > "".join(only_folders).count("-")


def directory_contains_resources(directory_path: str, source_only=False) -> bool:
    """
    Return True if the given directory contains at least one
    supported resource file (checked via file extension), or False
    otherwise.

    :param source_only:
        If True, only check for source-only formats.
    """
    resource_check = is_source_resource if source_only else is_resource
    for root, dirnames, filenames in os.walk(directory_path):
        # first() avoids checking past the first matching resource.
        if first(filenames, resource_check) is not None:
            return True
    return False


def locale_directory_path(
    checkout_path: str, locale_code: str, parent_directories: list[str]
) -> str:
    """
    Path to the directory where strings for the given locale are
    stored.
    """

    # Check paths that use underscore as locale/country code separator
    locale_code_variants = [locale_code, locale_code.replace("-", "_")]

    # Optimization for directories with a lot of paths: if parent_directories
    # is provided, we simply join it with locale_code and check if path exists
    possible_paths = [
        path
        for path in (
            os.path.join(parent_directory, locale)
            for locale in locale_code_variants
            for parent_directory in parent_directories
        )
        if os.path.exists(path)
    ] or [
        os.path.join(root, locale)
        for locale in locale_code_variants
        for root, dirnames, filenames in os.walk(checkout_path)
        if locale in dirnames
    ]

    for possible_path in possible_paths:
        if directory_contains_resources(possible_path):
            return possible_path

    # If locale directory empty (asymmetric formats)
    if possible_paths:
        return possible_paths[0]

    raise OSError(f"Directory for locale `{locale_code or 'source'}` not found")


def locale_to_source_path(path: str) -> str:
    """
    Return source resource path for the given locale resource path.
    Source files for .po files are actually .pot.
    """
    return path + "t" if path.endswith("po") else path


def source_to_locale_path(path: str) -> str:
    """
    Return locale resource path for the given source resource path.
    Locale files for .pot files are actually .po.
    """
    return path[:-1] if path.endswith("pot") else path


def escape_apostrophes(value: str) -> str:
    """
    Apostrophes (straight single quotes) have special meaning in Android strings.xml files,
    so they need to be escaped using a preceding backslash.

    Learn more:
    https://developer.android.com/guide/topics/resources/string-resource.html#escaping_quotes
    """
    return value.replace("'", "\\'")


def unescape_apostrophes(value: str) -> str:
    return value.replace("\\'", "'")


def escape_quotes(value: str) -> str:
    """
    DTD files can use single or double quotes for identifying strings,
    so &quot; and &apos; are the safe bet that will work in both cases.
    """
    value = value.replace('"', "\\&quot;")
    value = value.replace("'", "\\&apos;")

    return value


def unescape_quotes(value: str) -> str:
    value = value.replace("\\&quot;", '"')
    value = value.replace("\\u0022", '"')  # Bug 1390111
    value = value.replace('\\"', '"')

    value = value.replace("\\&apos;", "'")
    value = value.replace("\\u0027", "'")  # Bug 1390111
    value = value.replace("\\'", "'")

    return value


def create_parent_directory(path: str) -> None:
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
