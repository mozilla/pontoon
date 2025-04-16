"""
Parsing resource files.
"""

from os.path import splitext

from moz.l10n.formats import Format, detect_format, l10n_extensions
from moz.l10n.message import serialize_message
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import (
    ftl,
    json_extensions,
    json_keyvalue,
    po,
    xliff,
    xml,
)

from .common import ParseError, VCSTranslation


def are_compatible_files(file_a, file_b):
    """
    Return True if the given file names correspond to the same file format.
    Note that some formats (e.g. Gettext, XLIFF) use multiple file name patterns.
    """
    _, ext_a = splitext(file_a)
    _, ext_b = splitext(file_b)
    if ext_a in l10n_extensions and ext_b in l10n_extensions:
        if ext_a == ext_b:
            return True
        fmt_a = detect_format(file_a)
        fmt_b = detect_format(file_b)
        return fmt_a is not None and fmt_a == fmt_b
    return False


def parse_translations(path: str) -> list[VCSTranslation]:
    """
    Parse the resource file at the given path and return a
    list of translations.

    To add support for a new resource format,
    add it to moz.l10n: https://github.com/mozilla/moz-l10n

    :param path:
        Path to the resource file to parse.
    """
    if path.endswith(".ftl"):
        return ftl.parse(path)
    try:
        res = parse_resource(path)
    except Exception as err:
        raise ParseError(f"Could not parse {path}") from err
    match res.format:
        case Format.po:
            return po.parse(res)
        case Format.android:
            return xml.parse(res)
        case Format.xliff:
            return xliff.parse(res)
        case Format.webext:
            return json_extensions.parse(res)
        case Format.plain_json:
            return json_keyvalue.parse(res)
        case _:
            return [
                VCSTranslation(
                    key=entry.id[0],
                    context=entry.id[0],
                    order=order,
                    strings={
                        None: (string := serialize_message(res.format, entry.value))
                    },
                    source_string=string,
                    comments=entry.comment.split("\n") if entry.comment else None,
                )
                for order, entry in enumerate(res.all_entries())
            ]
