from json import dumps

from moz.l10n.formats.fluent import fluent_parse_entry, fluent_serialize_message
from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message
from moz.l10n.model import (
    CatchallKey,
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
    VariableRef,
)

from pontoon.base.models import Resource


def get_simple_preview(format: str, msg: str | Message | Pattern) -> str:
    """
    Flatten a message entry as a simple string.

    For multi-variant messages, selects the fallback variant.

    For Fluent, selects the value if it's not empty,
    or the first non-empty attribute.
    """
    if format == Resource.Format.FLUENT:
        if isinstance(msg, str):
            try:
                entry = fluent_parse_entry(msg, with_linepos=False)
                msg = (
                    entry.value
                    if not entry.value.is_empty()
                    else next(
                        prop
                        for prop in entry.properties.values()
                        if not prop.is_empty()
                    )
                )
            except Exception:
                return msg
        pattern = as_simple_pattern(msg)
        return fluent_serialize_message(PatternMessage(pattern))

    if format in (
        Resource.Format.ANDROID,
        Resource.Format.GETTEXT,
        Resource.Format.WEBEXT,
        Resource.Format.XCODE,
        Resource.Format.XLIFF,
    ):
        if isinstance(msg, str):
            try:
                msg = mf2_parse_message(msg)
            except Exception:
                return msg
    elif isinstance(msg, str):
        return msg

    preview = ""
    for part in as_simple_pattern(msg):
        preview += preview_placeholder(part)
    return preview


def as_simple_pattern(msg: Message | Pattern) -> Pattern:
    if isinstance(msg, list):
        return msg
    if isinstance(msg, PatternMessage):
        return msg.pattern
    return next(
        pattern
        for keys, pattern in msg.variants.items()
        if all(isinstance(key, CatchallKey) for key in keys)
    )


def preview_placeholder(part: str | Expression | Markup) -> str:
    if isinstance(part, str):
        return part
    if isinstance(ps := part.attributes.get("source", None), str):
        return ps
    if isinstance(part, Expression):
        if part.function == "html" and isinstance(part.arg, str):
            return part.arg
        elif part.function == "entity" and isinstance(part.arg, VariableRef):
            return part.arg.name
    elif part.kind in ("open", "standalone"):
        res = "<" + part.name
        for name, val in part.options.items():
            valstr = dumps(val) if isinstance(val, str) else "$" + val.name
            res += f" {name}={valstr}"
        res += ">" if part.kind == "open" else " />"
        return res
    elif part.kind == "close" and not part.options:
        return f"</{part.name}>"

    # Fallback; this is an error
    return mf2_serialize_message(PatternMessage([part]))
