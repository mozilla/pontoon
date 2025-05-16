"""
Parser for the .json translation format as used by the WebExtensions API:
https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization

See also:
https://www.chromium.org/developers/design-documents/extensions/how-the-extension-system-works/i18n
"""

from __future__ import annotations

from moz.l10n.formats.webext import webext_serialize_message
from moz.l10n.model import Entry, Message, Resource

from .common import VCSTranslation


def parse(res: Resource[Message]):
    return [
        as_translation(order, entry) for order, entry in enumerate(res.all_entries())
    ]


def as_translation(order: int, entry: Entry):
    assert len(entry.id) == 1
    key = entry.id[0]
    string, placeholders = webext_serialize_message(entry.value)
    return VCSTranslation(
        key=key,
        context=key,
        order=order,
        string=string or None,
        source_string=string,
        comments=[entry.comment] if entry.comment else None,
        source=placeholders,
    )
