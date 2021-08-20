"""
Parser for to pofile translation format.
"""
from datetime import datetime

from django.utils import timezone

import polib

from pontoon.sync import KEY_SEPARATOR
from pontoon.sync.exceptions import ParseError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation


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
            key = context + KEY_SEPARATOR + key

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

    def update_entry(self, locale):
        """Update the POEntry associated with this translation."""
        if self.po_entry.msgstr_plural:
            self.po_entry.msgstr_plural = {
                plural_form: self.strings.get(plural_form, "")
                for plural_form in range(locale.nplurals or 1)
            }
        else:
            self.po_entry.msgstr = self.strings.get(None, "")

        if self.fuzzy and "fuzzy" not in self.po_entry.flags:
            self.po_entry.flags.append("fuzzy")
        elif not self.fuzzy and "fuzzy" in self.po_entry.flags:
            self.po_entry.flags.remove("fuzzy")

    def __repr__(self):
        return "<POEntity {key}>".format(key=self.key.encode("utf-8"))


class POResource(ParsedResource):
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

    def save(self, locale):
        for entity in self.translations:
            entity.update_entry(locale)

        metadata = self.pofile.metadata
        if len(self.translations) > 0:
            latest_translation = max(
                self.translations,
                key=lambda t: t.last_updated or timezone.make_aware(datetime.min),
            )
            if latest_translation.last_updated:
                metadata["PO-Revision-Date"] = latest_translation.last_updated.strftime(
                    "%Y-%m-%d %H:%M%z"
                )
            if latest_translation.last_translator:
                metadata[
                    "Last-Translator"
                ] = latest_translation.last_translator.display_name_and_email

        metadata.update(
            {
                "Language": locale.code.replace("-", "_"),
                "X-Generator": "Pontoon",
                "Plural-Forms": (
                    "nplurals={locale.nplurals}; plural={locale.plural_rule};".format(
                        locale=locale
                    )
                ),
            }
        )

        self.pofile.save()

    def __repr__(self):
        return f"<POResource {self.pofile.fpath}>"


def parse(path, source_path=None, locale=None):
    try:
        pofile = polib.pofile(path, wrapwidth=200)
    except OSError as err:
        raise ParseError(f"Failed to parse {path}: {err}")

    return POResource(pofile)
