"""
Parsing resource files.
"""

from fnmatch import fnmatch
from os.path import basename, splitext

from pontoon.sync.formats import (
    ftl,
    json_extensions,
    json_keyvalue,
    po,
    silme,
    xliff,
    xml,
)
from pontoon.sync.formats.common import VCSTranslation


# To add support for a new resource format, add an entry to this dict
# where the key is the extension you're parsing and the value is a
# callable returning a list of VCSTranslation.
_SUPPORTED_FORMAT_PARSERS = {
    "*.dtd": silme.parse_dtd,
    "*.ftl": ftl.parse,
    "*.inc": silme.parse_inc,
    "*.ini": silme.parse_ini,
    "*messages.json": json_extensions.parse,
    "*.json": json_keyvalue.parse,
    "*.po": po.parse,
    "*.pot": po.parse,
    "*.properties": silme.parse_properties,
    "*.xlf": xliff.parse,
    "*.xliff": xliff.parse,
    "*.xml": xml.parse,
}


def _get_format_parser(file_name):
    for format, parser in _SUPPORTED_FORMAT_PARSERS.items():
        if fnmatch(file_name, format):
            return parser
    return None


def are_compatible_files(file_a, file_b):
    """
    Return True if the given file names correspond to the same file format.
    Note that some formats (e.g. Gettext, XLIFF) use multiple file name patterns.
    """
    parser_a = _get_format_parser(file_a)
    parser_b = _get_format_parser(file_b)
    if parser_a:
        return parser_a == parser_b
    return False


def parse_translations(path, source_path=None) -> list[VCSTranslation]:
    """
    Parse the resource file at the given path and return a
    list of translations.

    :param path:
        Path to the resource file to parse.
    :param source_path:
        Path to the corresponding resource file in the source directory
        for the resource we're parsing. Asymmetric formats need this
        for saving. Defaults to None.
    """
    filename = basename(path)
    parse_format = _get_format_parser(filename)
    if parse_format is None:
        raise ValueError(f"Translation format {splitext(path)[1]} is not supported.")
    return parse_format(path, source_path=source_path)
