import json
import logging
import re
from os.path import dirname, join

from pontoon.base.models import Locale

log = logging.getLogger(__name__)
_quotes: dict[str, list[str]] = None


def get_quotes(locale: Locale) -> tuple[str, str]:
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


def fix_punctuation(text: str, locale: Locale):
    """
    In particular when dealing with HTML content,
    machine translation may add extra spaces around inline `<elements>`.
    For punctuation, we can fix that in a locale-appropriate manner.
    While there is a risk that this may introduce some unwanted side effects,
    in general the output is improved.
    """
    # double quotes
    def fix_quotes(match: re.Match[str]):
        start, end = get_quotes(locale)
        return start + match.group(1).strip() + end

    text = re.sub(r"&quot;(.*?)&quot;", fix_quotes, text)
    text = re.sub(r"[„“](.*?)[“”]", fix_quotes, text)
    text = re.sub(r"«(.*?)»", fix_quotes, text)

    # single quote
    text = text.replace("&#39;", "’")

    # brackets
    text = re.sub(r"(?s)([\(\[]) *(.*?) *([\)\]])", r"\1\2\3", text)

    # spaces before general punctuation
    lc = locale.code
    if lc == "fr" or lc == "fr-BE" or lc == "fr-CA" or lc == "fr-CH" or lc == "fr-FR":
        # https://fr.wikipedia.org/wiki/Ponctuation#En_français
        text = re.sub(r"(</\w+>) +([,.])", r"\1\2", text)
        text = re.sub(r" +([:;!?%#-])", "\u202f\\1", text)
    else:
        text = re.sub(r"(</\w+>) +([,.:;·!?~՞؟،%#-])", r"\1\2", text)

    return text
