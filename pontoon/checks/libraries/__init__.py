from . import compare_locales
from . import translate_toolkit
from . import pontoon_db, pontoon_non_db


def run_checks(
    entity, locale_code, original, string, use_tt_checks,
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
    pontoon_db_checks = pontoon_db.run_checks(entity, original, string)
    pontoon_non_db_checks = pontoon_non_db.run_checks(entity, string)

    try:
        cl_checks = compare_locales.run_checks(entity, locale_code, string)
    except compare_locales.UnsupportedStringError:
        cl_checks = None
    except compare_locales.UnsupportedResourceTypeError:
        cl_checks = None

    tt_checks = {}
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
        elif resource_ext == "lang":
            tt_disabled_checks.update(["newlines"])

        tt_checks = translate_toolkit.run_checks(
            original, string, locale_code, tt_disabled_checks
        )

    checks = dict(tt_checks, **(cl_checks or {}))

    checks.update(pontoon_db_checks)
    checks.update(pontoon_non_db_checks)

    return checks
