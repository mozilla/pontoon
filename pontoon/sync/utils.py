import os

from pontoon.base.models import Resource
from pontoon.base.utils import extension_in, first


def is_in_hidden_directory(path):
    """
    Return true if path contains hidden directory.
    """
    for p in path.split(os.sep):
        if p.startswith('.'):
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


def directory_contains_resources(directory_path, source_only=False):
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


def locale_directory_path(checkout_path, locale_code):
    """
    Path to the directory where strings for the given locale are
    stored.
    """
    possible_paths = []
    for root, dirnames, filenames in os.walk(checkout_path):
        if locale_code in dirnames:
            possible_paths.append(os.path.join(root, locale_code))

        locale_variant = locale_code.replace('-', '_')
        if locale_variant in dirnames:
            possible_paths.append(os.path.join(root, locale_variant))

    for possible_path in possible_paths:
        if directory_contains_resources(possible_path):
            return possible_path

    if possible_paths:
        return possible_paths[0]

    raise IOError('Directory for locale `{0}` not found'.format(
                  locale_code or 'source'))


def relative_source_path(path):
    """
    Return relative source resource path for the given relative locale
    resource path. Source files for .po files are actually .pot.
    """
    if path.endswith('po'):
        path += 't'
    return path
