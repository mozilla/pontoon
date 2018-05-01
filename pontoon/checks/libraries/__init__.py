from __future__ import absolute_import

from django.http import JsonResponse

from . import compare_locales
from . import translate_toolkit
from . import pontoon


def run_checks(
    entity,
    locale,
    original,
    string,
    use_tt_checks,
    ignore_warnings,
):
    """
    Main function that performs all quality checks from frameworks handled in Pontoon.

    :arg pontoon.base.models.Entity entity: Source entity
    :arg pontoon.base.models.Locale locale: Locale of a translation
    :arg basestring original: an original string
    :arg basestring string: a translation
    :arg bool use_tt_checks: use Translate Toolkit checks
    :arg bool ignore_warnings: removes warnings from failed checks

    :return: Return types:
        * JsonResponse - If there are errors
        * None - If there's no errors and non-omitted warnings.
    """
    try:
        cl_checks = compare_locales.run_checks(entity, locale.code, string)
    except compare_locales.UnsupportedResourceTypeError:
        cl_checks = None

    pontoon_checks = pontoon.run_checks(entity, string)

    tt_checks = {}
    resource_ext = entity.resource.format

    if use_tt_checks and resource_ext != 'ftl':
        tt_disabled_checks = set()

        # Some compare-locales checks overlap with Translate Toolkit checks
        if cl_checks is not None:
            if resource_ext == 'properties':
                tt_disabled_checks = {
                    'escapes',
                    'nplurals',
                    'printf'
                }
        elif resource_ext == 'lang':
            tt_disabled_checks = {
                'newlines',
            }

        if resource_ext not in {'properties', 'ini', 'dtd'} and string == '':
            tt_disabled_checks.add('untranslated')

        tt_checks = translate_toolkit.run_checks(
            original, string, locale, tt_disabled_checks
        )

    checks = dict(
        tt_checks,
        **(cl_checks or {})
    )

    checks.update(pontoon_checks)

    has_errors = any(p.endswith('Errors') for p in checks)

    if (not ignore_warnings and checks) or has_errors:
        return JsonResponse({
            'failedChecks': checks,
        })
