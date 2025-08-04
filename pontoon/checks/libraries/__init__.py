from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_pattern
from moz.l10n.model import CatchallKey, Pattern, PatternMessage, SelectMessage

from . import compare_locales, pontoon_db, pontoon_non_db, translate_toolkit


def as_gettext(pattern: Pattern) -> str:
    s = "".join(mf2_serialize_pattern(pattern))
    return s.replace(r"\{", "{").replace(r"\}", "}")


def run_checks(
    entity,
    locale_code,
    original,
    string,
    use_tt_checks,
):
    """
    Main function that performs all quality checks from frameworks handled in Pontoon.

    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring locale_code: Locale code of a translation
    :arg basestring original: an original string
    :arg basestring string: a translation
    :arg bool use_tt_checks: use Translate Toolkit checks

    :return: Return types:
        * JsonResponse - If there are errors
        * None - If there's no errors and non-omitted warnings.
    """
    checks = {}
    checks.update(pontoon_db.run_checks(entity, original, string))
    checks.update(pontoon_non_db.run_checks(entity, string))

    try:
        cl_checks = compare_locales.run_checks(entity, locale_code, string)
        checks.update(cl_checks)
    except (
        compare_locales.UnsupportedStringError,
        compare_locales.UnsupportedResourceTypeError,
    ):
        cl_checks = None

    resource_ext = entity.resource.format

    if use_tt_checks and resource_ext != "ftl":
        # Always disable checks we don't use. For details, see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1410619
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1514691
        tt_disabled_checks = {
            "acronyms",
            "gconf",
            "kdecomments",
            "untranslated",
        }

        # Some compare-locales checks overlap with Translate Toolkit checks
        if cl_checks is not None:
            if resource_ext == "properties":
                tt_disabled_checks.update(["escapes", "nplurals", "printf"])
            elif resource_ext == "xml":
                tt_disabled_checks.update(
                    [
                        "doublespacing",
                        "endwhitespace",
                        "escapes",
                        "newlines",
                        "numbers",
                        "printf",
                        "singlequoting",
                        "startwhitespace",
                    ]
                )

        tt_patterns: list[tuple[str, str]] = []
        if resource_ext == "po":
            src_msg = mf2_parse_message(original)
            tgt_msg = mf2_parse_message(string)
            if isinstance(src_msg, SelectMessage):
                s0 = as_gettext(src_msg.variants[(CatchallKey(),)])
                if isinstance(tgt_msg, SelectMessage):
                    for keys, pattern in tgt_msg.variants.items():
                        if keys == ("one",):
                            src = as_gettext(src_msg.variants[keys])
                        else:
                            src = s0
                        tt_patterns.append((src, as_gettext(pattern)))
                else:
                    tt_patterns.append((s0, as_gettext(tgt_msg.pattern)))
            elif isinstance(tgt_msg, PatternMessage):
                tt_patterns.append(
                    (as_gettext(src_msg.pattern), as_gettext(tgt_msg.pattern))
                )
        else:
            tt_patterns.append((original, string))
        tt_warnings = {}
        for src, tgt in tt_patterns:
            tt_checks = translate_toolkit.run_checks(
                src, tgt, locale_code, tt_disabled_checks
            )
            if tt_checks:
                tt_warnings.update((w, None) for w in tt_checks["ttWarnings"])
        if tt_warnings:
            checks["ttWarnings"] = list(tt_warnings)

    return checks
