"""
Parsing resource files.
"""

from os.path import splitext

from moz.l10n.formats import Format, detect_format, l10n_extensions
from moz.l10n.message import serialize_message
from moz.l10n.model import Message, Resource as MozL10nResource

from pontoon.sync.formats import (
    ftl,
    gettext,
    json_extensions,
    json_keyvalue,
    properties,
    xliff,
    xml,
)

from .common import VCSTranslation


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


def as_vcs_translations(res: MozL10nResource[Message]) -> list[VCSTranslation]:
    match res.format:
        case Format.fluent:
            return ftl.parse(res)
        case Format.gettext:
            return gettext.parse(res)
        case Format.properties:
            return properties.parse(res)
        case Format.android:
            return xml.parse(res)
        case Format.xliff:
            return xliff.parse(res)
        case Format.webext:
            return json_extensions.parse(res)
        case Format.plain_json:
            return json_keyvalue.parse(res)
        # Currently this includes .dtd, and .ini support.
        # https://github.com/mozilla/moz-l10n/blob/v0.7.0/python/moz/l10n/formats/__init__.py#L32-L47
        case _:
            return [
                VCSTranslation(
                    key=entry.id[0],
                    context=entry.id[0],
                    order=order,
                    string=(string := serialize_message(res.format, entry.value)),
                    source_string=string,
                    comments=entry.comment.split("\n") if entry.comment else None,
                )
                for order, entry in enumerate(res.all_entries())
            ]
