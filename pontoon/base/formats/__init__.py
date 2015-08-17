"""
Parsing resource files.

See base.py for the ParsedResource base class.
"""
import os.path

from pontoon.base.formats import lang, po


# To add support for a new resource format, add an entry to this dict
# where the key is the extension you're parsing and the value is a
# callable returning an instance of a ParsedResource subclass.
SUPPORTED_FORMAT_PARSERS = {
    '.lang': lang.parse,
    '.po': po.parse,
    '.pot': po.parse,
}


def parse(path):
    """
    Parse the resource file at the given path and return a
    ParsedResource with its translations.
    """
    root, extension = os.path.splitext(path)
    if extension in SUPPORTED_FORMAT_PARSERS:
        return SUPPORTED_FORMAT_PARSERS[extension](path)
    else:
        raise ValueError('Translation format {0} is not supported.'
                         .format(extension))
