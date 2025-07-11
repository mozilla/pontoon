"""
Parser for the .json translation format as used by the WebExtensions API:
https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization

See also:
https://www.chromium.org/developers/design-documents/extensions/how-the-extension-system-works/i18n
"""

from __future__ import annotations

from datetime import datetime

from moz.l10n.formats.webext import webext_serialize_message
from moz.l10n.model import Entry, Message

from pontoon.base.models import Entity

from .common import VCSTranslation


def webext_as_translation(entry: Entry):
    assert len(entry.id) == 1
    string, _ = webext_serialize_message(entry.value)
    return VCSTranslation(key=entry.id[0], string=string or None)


def webext_as_entity(entry: Entry[Message], now: datetime) -> Entity:
    assert len(entry.id) == 1
    key = entry.id[0]
    string, placeholders = webext_serialize_message(entry.value)
    return Entity(
        key=key,
        context=key,
        string=string,
        comment=entry.comment,
        source=placeholders,
        date_created=now,
    )
