"""
Parser for to pofile translation format.
"""

import polib

from .common import ParseError, VCSTranslation


def parse_po_entry(po_entry: polib.POEntry, order: int):
    # Pofiles use the source as the key prepended with context if available.
    key = po_entry.msgid
    context = po_entry.msgctxt or ""
    if context:
        key = context + "\x04" + key

    if po_entry.msgstr_plural:
        strings = {key: value for key, value in po_entry.msgstr_plural.items() if value}
    else:
        strings = {None: po_entry.msgstr} if po_entry.msgstr else {}

    return VCSTranslation(
        key=key,
        context=context,
        order=order,
        strings=strings,
        source_string=po_entry.msgid,
        source_string_plural=po_entry.msgid_plural,
        comments=po_entry.comment.split("\n") if po_entry.comment else None,
        fuzzy="fuzzy" in po_entry.flags,
        source=po_entry.occurrences,
    )


def parse(path, source_path=None):
    try:
        pofile = polib.pofile(path, wrapwidth=200)
    except OSError as err:
        raise ParseError(f"Failed to parse {path}: {err}")

    return [
        parse_po_entry(entry, k) for k, entry in enumerate(pofile) if not entry.obsolete
    ]
