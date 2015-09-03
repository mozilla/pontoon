"""
Parsing resource files.

See base.py for the ParsedResource base class.
"""
import os.path

from pontoon.base.formats import lang, po, silme, xliff


# To add support for a new resource format, add an entry to this dict
# where the key is the extension you're parsing and the value is a
# callable returning an instance of a ParsedResource subclass.
SUPPORTED_FORMAT_PARSERS = {
    '.lang': lang.parse,
    '.po': po.parse,
    '.pot': po.parse,
    '.xliff': xliff.parse,
    '.dtd': silme.parse_dtd,
    '.properties': silme.parse_properties,
    '.ini': silme.parse_ini,
}


def parse(path, source_path=None):
    """
    Parse the resource file at the given path and return a
    ParsedResource with its translations.

    :param path:
        Path to the resource file to parse.
    :param source_path:
        Path to the corresponding resource file in the source directory
        for the resource we're parsing. Asymmetric formats need this
        for saving. Defaults to None.
    """
    root, extension = os.path.splitext(path)
    if extension in SUPPORTED_FORMAT_PARSERS:
        return SUPPORTED_FORMAT_PARSERS[extension](path, source_path=source_path)
    else:
        raise ValueError('Translation format {0} is not supported.'
                         .format(extension))
