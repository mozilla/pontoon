from json import dumps

from moz.l10n.formats import Format
from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message
from moz.l10n.message import serialize_message
from moz.l10n.model import (
    CatchallKey,
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
    VariableRef,
)

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
                msg = as_pattern_message(msg)
                return serialize_message(Format.fluent, msg)

            case Resource.Format.ANDROID:
                msg = mf2_parse_message(string)
                return android_simple_preview(msg)

            case Resource.Format.GETTEXT:
                msg = mf2_parse_message(string)
                msg = as_pattern_message(msg)
                return serialize_message(None, msg)
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


def android_simple_preview(msg: Message | Pattern) -> str:
    """
    Matches the JS androidEditPattern() from translate/src/utils/message/android.ts
    """
    preview = ""
    pattern = msg if isinstance(msg, list) else as_pattern_message(msg).pattern
    for part in pattern:
        preview += android_placeholder_preview(part)
    return preview


def android_placeholder_preview(part: str | Expression | Markup) -> str:
    if isinstance(part, str):
        return part
    if isinstance(ps := part.attributes.get("source", None), str):
        return ps
    if isinstance(part, Expression):
        if part.function == "html" and isinstance(part.arg, str):
            return part.arg
        elif part.function == "entity" and isinstance(part.arg, VariableRef):
            return part.arg.name
    elif part.kind == "open":
        res = "<" + part.name
        for name, val in part.options.items():
            valstr = dumps(val) if isinstance(val, str) else "$" + val.name
            res += f" {name}={valstr}"
        res += ">"
        return res
    elif part.kind == "close" and not part.options:
        return f"</{part.name}>"

    # Fallback; this is an error
    return mf2_serialize_message(PatternMessage([part]))
