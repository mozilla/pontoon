"""
Parser for to pofile translation format.
"""

import polib

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.vcs.translation import VCSTranslation


class POEntity(VCSTranslation):
    def __init__(self, po_entry, order):
        self.po_entry = po_entry

        if po_entry.msgstr_plural:
            strings = po_entry.msgstr_plural
        else:
            strings = {None: po_entry.msgstr}

        # Remove empty strings from the string dict.
        strings = {key: value for key, value in strings.items() if value}

        # Pofiles use the source as the key prepended with context if available.
        key = po_entry.msgid
        context = po_entry.msgctxt or ""
        if context:
            key = context + "\x04" + key

        super().__init__(
            key=key,
            context=context,
            source_string=po_entry.msgid,
            source_string_plural=po_entry.msgid_plural,
            strings=strings,
            comments=po_entry.comment.split("\n") if po_entry.comment else [],
            fuzzy="fuzzy" in po_entry.flags,
            order=order,
            source=po_entry.occurrences,
        )

    def __repr__(self):
        return "<POEntity {key}>".format(key=self.key.encode("utf-8"))


class POResource(ParsedResource):
    entities: list[POEntity]

    def __init__(self, pofile):
        self.pofile = pofile
        self.entities = [
            POEntity(entry, k)
            for k, entry in enumerate(self.pofile)
            if not entry.obsolete
        ]

    @property
    def translations(self):
        return self.entities

    def __repr__(self):
        return f"<POResource {self.pofile.fpath}>"


def parse(path, source_path=None, locale=None):
    try:
        pofile = polib.pofile(path, wrapwidth=200)
    except OSError as err:
        raise ParseError(f"Failed to parse {path}: {err}")

    return POResource(pofile)
