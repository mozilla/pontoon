from django.http import JsonResponse

import compare_locales
import translate_toolkit
from . import pontoon


def run_checks(
    entity,
    locale,
    original,
    string,
    ignore_warnings,
    same
):
    """
    Main function that performs all quality checks from frameworks handled in Pontoon.

    :arg pontoon.base.models.Entity entity: Source entity
    :arg pontoon.base.models.Locale locale: Locale of a translation
    :arg basestring original: an original string
    :arg basestring string: a translation
    :arg bool ignore_warnings: removes warnings from failed checks
    :arg bool same: if a translation exists in the database and can't be submitted

    :return: Return types:
        * JsonResponse - If there are errors
        * None - If there's no errors and non-omitted warnings.
    """
    try:
        cl_checks = compare_locales.run_checks(entity, locale.code, string)
    except compare_locales.UnsupportedResourceTypeError:
        cl_checks = None

    resource_ext = entity.resource.format

    # Some of checks from compare-locales overlap checks from Translate Toolkit
    tt_disabled_checks = set()

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

    pontoon_checks = pontoon.run_checks(entity, string)

    tt_checks = translate_toolkit.run_checks(original, string, locale, tt_disabled_checks)

    checks = dict(
        # User decided to ignore checks from Translation Toolkit
        tt_checks,
        **(cl_checks or {})
    )

    checks.update(pontoon_checks)

    has_errors = any(p.endswith('Errors') for p in checks)

    if (not ignore_warnings and checks) or has_errors or same:
        return JsonResponse({
            'failedChecks': checks,
            'same': same,
        })
