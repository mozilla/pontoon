from translate.filters import checks
from translate.lang import data as lang_data
from translate.storage import base as storage_base


def run_checks(original, string, locale_code, disabled_checks=None):
    """Check for obvious errors like blanks and missing interpunction."""
    original = lang_data.normalized_unicode(original)
    string = lang_data.normalized_unicode(string)
    disabled_checks = disabled_checks or []

    unit = storage_base.TranslationUnit(original)
    unit.target = string
    checker = checks.StandardChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage=locale_code),
        excludefilters=disabled_checks,
    )

    warnings = checker.run_filters(unit)

    if not warnings:
        return {}

    check_names = {
        "accelerators": "Accelerators",
        "blank": "Blank",
        "brackets": "Brackets",
        "compendiumconflicts": "Compendium conflict",
        "credits": "Translator credits",
        "doublequoting": "Double quotes",
        "doublespacing": "Double spaces",
        "doublewords": "Repeated word",
        "emails": "E-mail",
        "endpunc": "Ending punctuation",
        "endwhitespace": "Ending whitespace",
        "escapes": "Escapes",
        "filepaths": "File paths",
        "functions": "Functions",
        "long": "Long",
        "musttranslatewords": "Must translate words",
        "newlines": "Newlines",
        "nplurals": "Number of plurals",
        "notranslatewords": "Don't translate words",
        "numbers": "Numbers",
        "options": "Options",
        "printf": "Printf format string mismatch",
        "puncspacing": "Punctuation spacing",
        "purepunc": "Pure punctuation",
        "sentencecount": "Number of sentences",
        "short": "Short",
        "simplecaps": "Simple capitalization",
        "simpleplurals": "Simple plural(s)",
        "singlequoting": "Single quotes",
        "startcaps": "Starting capitalization",
        "startpunc": "Starting punctuation",
        "startwhitespace": "Starting whitespace",
        "tabs": "Tabs",
        "unchanged": "Unchanged",
        "urls": "URLs",
        "validchars": "Valid characters",
        "variables": "Placeholders",
        "xmltags": "XML tags",
    }

    warnings_array = []
    for key in warnings.keys():
        warning = check_names.get(key, key)
        warnings_array.append(warning)

    return {
        "ttWarnings": warnings_array,
    }
