from typing import Any

from moz.l10n.formats.fluent import fluent_parse_entry, fluent_serialize_entry
from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message
from moz.l10n.formats.properties import (
    properties_parse_message,
    properties_serialize_message,
)
from moz.l10n.message import message_to_json, serialize_message
from moz.l10n.model import CatchallKey, Entry, Message, SelectMessage

from pontoon.base.models import Entity, Resource


JsonMessage = list[Any] | dict[str, Any]


def parse_db_string_to_json(
    res_format: str,
    source: str,
) -> tuple[JsonMessage, dict[str, JsonMessage] | None]:
    match res_format:
        case Resource.Format.FLUENT:
            fe = fluent_parse_entry(source)
            value = message_to_json(fe.value)
            properties = {
                name: message_to_json(prop) for name, prop in fe.properties.items()
            } or None
            return value, properties
        case (
            Resource.Format.ANDROID
            | Resource.Format.GETTEXT
            | Resource.Format.WEBEXT
            | Resource.Format.XCODE
            | Resource.Format.XLIFF
        ):
            msg = mf2_parse_message(source)
            # MF2 syntax does not retain the catchall name/label
            if isinstance(msg, SelectMessage):
                for keys in msg.variants:
                    for key in keys:
                        if isinstance(key, CatchallKey):
                            key.value = "other"
            return message_to_json(msg), None
        case Resource.Format.PROPERTIES:
            msg = properties_parse_message(source)
            return message_to_json(msg), None
        case _:
            return [source] if source else [], None


def serialize_for_db(
    entity: Entity, value: Message, properties: dict[str, Message]
) -> str:
    match entity.resource.format:
        case Resource.Format.FLUENT:
            entry = Entry(tuple(entity.key), value, properties)
            return fluent_serialize_entry(entry)
        case (
            Resource.Format.ANDROID
            | Resource.Format.GETTEXT
            | Resource.Format.WEBEXT
            | Resource.Format.XCODE
            | Resource.Format.XLIFF
        ):
            return mf2_serialize_message(value)
        case Resource.Format.PROPERTIES:
            return properties_serialize_message(value)
        case _:
            return serialize_message(None, value)
