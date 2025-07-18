"""
Parsing resource files.
"""

from datetime import datetime
from os.path import splitext

from moz.l10n.formats import Format, detect_format, l10n_extensions
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Id as L10nId, Message, Resource as MozL10nResource

from pontoon.base.models import Entity

from .common import VCSTranslation
from .ftl import ftl_as_entity, ftl_as_translation
from .gettext import gettext_as_entity, gettext_as_translation
from .json_extensions import webext_as_entity, webext_as_translation
from .json_keyvalue import plain_json_as_entity, plain_json_as_translation
from .properties import properties_as_entity, properties_as_translation
from .xliff import xliff_as_entity, xliff_as_translation
from .xml import android_as_entity, android_as_translation


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
    translations: list[VCSTranslation] = []
    for section in res.sections:
        if res.format == Format.android and section.id:
            continue
        for entry in section.entries:
            if not isinstance(entry, Entry):
                continue
            match res.format:
                case Format.fluent:
                    tx = ftl_as_translation(entry)
                case Format.gettext:
                    tx = gettext_as_translation(entry)
                case Format.properties:
                    tx = properties_as_translation(entry)
                case Format.android:
                    tx = android_as_translation(entry)
                case Format.xliff:
                    tx = xliff_as_translation(section.id, entry)
                case Format.webext:
                    tx = webext_as_translation(entry)
                case Format.plain_json:
                    tx = plain_json_as_translation(entry)
                case _:
                    # Currently this includes .dtd, .inc, and .ini support.
                    # https://github.com/mozilla/moz-l10n/blob/v0.7.0/python/moz/l10n/formats/__init__.py#L32-L47
                    string = serialize_message(res.format, entry.value)
                    tx = VCSTranslation(key=entry.id, string=string)
            translations.append(tx)
    return translations


def as_entity(
    format: Format | None,
    section_id: L10nId,
    entry: Entry[Message],
    now: datetime,
) -> Entity:
    """Sets all required fields **except** `order`, `resource`, and `section`."""
    match format:
        case Format.fluent:
            entity = ftl_as_entity(entry, now)
        case Format.gettext:
            entity = gettext_as_entity(entry, now)
        case Format.properties:
            entity = properties_as_entity(entry, now)
        case Format.android:
            entity = android_as_entity(entry, now)
        case Format.xliff:
            entity = xliff_as_entity(section_id, entry, now)
        case Format.webext:
            entity = webext_as_entity(entry, now)
        case Format.plain_json:
            entity = plain_json_as_entity(entry, now)
        case _:
            # For Format.dtd and Format.ini
            entity = Entity(
                key=list(entry.id),
                string=serialize_message(format, entry.value),
                comment=entry.comment,
                date_created=now,
            )
    if entry.meta:
        entity.meta = [[m.key, m.value] for m in entry.meta]
    return entity
