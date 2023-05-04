import json
import logging
import re
from os.path import dirname, join
from typing import Tuple

from pontoon.base.models import Locale

log = logging.getLogger(__name__)
_quotes: dict[str, list[str]] = None


def get_quotes(locale: Locale) -> Tuple[str, str]:
    # Cache data
    global _quotes
    if _quotes is None:
        try:
            file = open(join(dirname(__file__), "static/locale-quotes.json"))
            _quotes = json.load(file)
        except Exception:
            log.error("Error loading locale-quotes.json")
            _quotes = {}

    # Exact match
    lc = locale.code
    if lc in _quotes:
        return tuple(_quotes[lc])

    # With or without script identifier
    res = None
    lc_parts = lc.split("-")
    if len(lc_parts) == 3:
        del lc_parts[1:2]
    else:
        # Not all scripts are tested, because data does not vary for all.
        # `Latn` is used as a fallback; it won't match for invalid cases.
        script = "Latn"
        if locale.script == "Arabic":
            script = "Arab"
        elif locale.script == "Cyrillic":
            script = "Cyrl"
        elif locale.script == "Simplified Chinese":
            script = "Hans"
        elif locale.script == "Traditional Chinese":
            script = "Hant"
        lc_parts[1:1] = [script]
    lc = "-".join(lc_parts)
    if lc in _quotes:
        res = _quotes[lc]

    # Language with script, no region
    if res is None and len(lc_parts) == 3:
        del lc_parts[2:]
        lc = "-".join(lc_parts)
        if lc in _quotes:
            res = _quotes[lc]

    # Main language tag only, with fallback to straight quotes
    if res is None:
        lc = lc_parts[0]
        res = _quotes[lc] if lc in _quotes else ['"', '"']

    _quotes[locale.code] = res
    return tuple(res)


def fix_quotes(text: str, locale: Locale):
    def fix(match: re.Match[str]):
        start, end = get_quotes(locale)
        return start + match.group(1).strip() + end

    text = re.sub(r"&quot;(.*?)&quot;", fix, text)
    text = re.sub(r"[„“](.*?)[“”]", fix, text)
    text = re.sub(r"«(.*?)»", fix, text)

    # Always use curly single quote
    text = text.replace("&#39;", "’")

    return text
