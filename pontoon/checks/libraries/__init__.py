from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_pattern
from moz.l10n.model import CatchallKey, Pattern, PatternMessage, SelectMessage

from pontoon.base.models import Entity, Resource
from pontoon.base.simple_preview import android_simple_preview

from . import compare_locales, translate_toolkit
from .custom import run_custom_checks


def as_gettext(pattern: Pattern) -> str:
    s = "".join(mf2_serialize_pattern(pattern))
    return s.replace(r"\{", "{").replace(r"\}", "}")


def run_checks(
    entity: Entity,
    locale_code: str,
    original: str,
    string: str,
    use_tt_checks: bool,
) -> dict[str, list[str]]:
    """
    Main function that performs all quality checks from frameworks handled in Pontoon.

    :arg bool use_tt_checks: use Translate Toolkit checks

    :return: Non-empty dict if there are errors or warnings
    """
    checks: dict[str, list[str]] = {}
    checks.update(run_custom_checks(entity, original, string))

    try:
        cl_checks = compare_locales.run_checks(entity, locale_code, string)
        checks.update(cl_checks)
    except (
        compare_locales.UnsupportedStringError,
        compare_locales.UnsupportedResourceTypeError,
    ):
        cl_checks = None

    res_format = entity.resource.format

    if use_tt_checks and res_format != Resource.Format.FLUENT:
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
            if res_format == Resource.Format.PROPERTIES:
                tt_disabled_checks.update(["escapes", "nplurals", "printf"])
            elif res_format == Resource.Format.ANDROID:
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
        match res_format:
            case Resource.Format.ANDROID:
                src_msg = mf2_parse_message(original)
                tgt_msg = mf2_parse_message(string)
                src0 = android_simple_preview(src_msg)
                if isinstance(src_msg, SelectMessage) and isinstance(
                    tgt_msg, SelectMessage
                ):
                    for keys, pattern in tgt_msg.variants.items():
                        src = (
                            android_simple_preview(src_msg.variants[keys])
                            if keys == ("one",)
                            else src0
                        )
                        tt_patterns.append((src, android_simple_preview(pattern)))
                else:
                    tt_patterns.append((src0, android_simple_preview(tgt_msg)))

            case Resource.Format.GETTEXT:
                src_msg = mf2_parse_message(original)
                tgt_msg = mf2_parse_message(string)
                if isinstance(src_msg, SelectMessage):
                    src0 = as_gettext(src_msg.variants[(CatchallKey(),)])
                    if isinstance(tgt_msg, SelectMessage):
                        for keys, pattern in tgt_msg.variants.items():
                            if keys == ("one",):
                                src = as_gettext(src_msg.variants[keys])
                            else:
                                src = src0
                            tt_patterns.append((src, as_gettext(pattern)))
                    else:
                        tt_patterns.append((src0, as_gettext(tgt_msg.pattern)))
                elif isinstance(tgt_msg, PatternMessage):
                    tt_patterns.append(
                        (as_gettext(src_msg.pattern), as_gettext(tgt_msg.pattern))
                    )

            case _:
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
