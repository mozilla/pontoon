import json
import logging
import re
from typing import Literal

from pontoon.base.models import Locale

log = logging.getLogger(__name__)

PluralCategory = Literal["zero", "one", "two", "few", "many", "other"]

# Locale code -> plural type -> category -> examples
_data: dict[
    str,
    dict[
        Literal["cardinal", "ordinal"],
        dict[PluralCategory, list[str]],
    ],
] = None


def get_plural_examples(locale: Locale):
    """
    Loads data from the npm package `make-plural`.
    """
    # Cache data
    global _data
    if _data is None:
        try:
            file = open("node_modules/make-plural/examples.json")
            _data = json.load(file)
        except Exception:
            log.error("Error loading plural examples")
            _data = {}

    # Exact match
    lc = locale.code
    if lc in _data:
        return _data[lc]["cardinal"]

    # Map to appropriate make-plural key
    if lc.startswith("pt-PT"):
        lc = "pt_PT"
    else:
        lc = re.sub(r"-.*$", "", lc)

    return _data[lc]["cardinal"] if lc in _data else {}


def find_plural_example(locale: Locale, cat: PluralCategory):
    # Shortcuts; these are valid for all known locales
    if cat == "zero":
        return "0"
    elif cat == "one":
        return "1"
    elif cat == "two":
        return "2"

    examples = get_plural_examples(locale)
    if cat != "few" and cat != "many":
        cat = "other"
    if cat in examples:
        cat_ex = examples[cat]
        if len(cat_ex) > 1 and cat_ex[0] == "0":
            return cat_ex[1]
        if cat_ex:
            return cat_ex[0]

    # Fallback; these are the most likely matches in CLDR data
    if cat == "few":
        return "3"
    elif cat == "many":
        return "11"
    else:
        return "14"
