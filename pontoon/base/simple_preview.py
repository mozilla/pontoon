from moz.l10n.formats import Format
from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.formats.mf2 import mf2_parse_message
from moz.l10n.message import serialize_message
from moz.l10n.model import CatchallKey, Message, PatternMessage, SelectMessage

from pontoon.base.models import Resource


def get_simple_preview(format: str, string: str):
    """
    Flatten a message entry as a simple string.

    For multi-variant messages, selects the fallback variant.

    For Fluent, selects the value if it's not empty,
    or the first non-empty attribute.
    """
    try:
        match format:
            case Resource.Format.FLUENT:
                entry = fluent_parse_entry(string, with_linepos=False)
                if not entry.value.is_empty():
                    msg = entry.value
                else:
                    msg = next(
                        prop
                        for prop in entry.properties.values()
                        if not prop.is_empty()
                    )
                flat_msg = as_pattern_message(msg)
                return serialize_message(Format.fluent, flat_msg)
            case Resource.Format.GETTEXT:
                msg = mf2_parse_message(string)
                flat_msg = as_pattern_message(msg)
                return serialize_message(None, flat_msg)
    except Exception:
        pass
    return string


def as_pattern_message(msg: Message) -> PatternMessage:
    if isinstance(msg, SelectMessage):
        default_pattern = next(
            pattern
            for keys, pattern in msg.variants.items()
            if all(isinstance(key, CatchallKey) for key in keys)
        )
        return PatternMessage(default_pattern)
    else:
        return msg
