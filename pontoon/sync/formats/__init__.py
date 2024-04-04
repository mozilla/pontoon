"""
Parsing resource files.

See base.py for the ParsedResource base class.
"""
import os.path
import fnmatch

from pontoon.sync.formats import (
    ftl,
    json_extensions,
    json_keyvalue,
    po,
    silme,
    xliff,
    xml,
)

# To add support for a new resource format, add an entry to this dict
# where the key is the extension you're parsing and the value is a
# callable returning an instance of a ParsedResource subclass.
SUPPORTED_FORMAT_PARSERS = {
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


def get_format_parser(file_name):
    for format, parser in SUPPORTED_FORMAT_PARSERS.items():
        if fnmatch.fnmatch(file_name, format):
            return parser
    return None


def are_compatible_files(file_a, file_b):
    """
    Return True if the given file names correspond to the same file format.
    Note that some formats (e.g. Gettext, XLIFF) use multiple file name patterns.
    """
    parser_a = get_format_parser(file_a)
    parser_b = get_format_parser(file_b)
    if parser_a:
        return parser_a == parser_b
    return False


def parse(path, source_path=None, locale=None):
    """
    Parse the resource file at the given path and return a
    ParsedResource with its translations.

    :param path:
        Path to the resource file to parse.
    :param source_path:
        Path to the corresponding resource file in the source directory
        for the resource we're parsing. Asymmetric formats need this
        for saving. Defaults to None.
    :param locale:
        Object which describes information about currently processed locale.
        Some of the formats require information about things like e.g. plural form.
    """
    filename = os.path.basename(path)
    parser = get_format_parser(filename)
    if parser:
        return parser(path, source_path=source_path, locale=locale)
    root, extension = os.path.splitext(path)
    raise ValueError(f"Translation format {extension} is not supported.")
