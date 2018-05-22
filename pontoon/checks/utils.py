from django.http import JsonResponse

from pontoon.checks.models import (
    Warning,
    Error
)

def save_failed_checks(translation, failed_checks):
    """
    Save all failed checks to Database
    :arg Translation translation: instance of translation
    ;arg dict failed_checks: dictionary with failed checks
    """
    warnings = []
    errors = []
    for check_group, messages in failed_checks.items():
        library = (
            check_group
            .replace('Warnings', '')
            .replace('Errors', '')
        )

        if check_group.endswith('Errors'):
            severity_cls, messages_list = Error, errors
        else:
            severity_cls, messages_list = Warning, warnings

        messages_list.extend([
            severity_cls(
                library=library,
                message=message,
                translation=translation,
            ) for message in messages
        ])

    if warnings:
        translation.warnings.all().delete()
        Warning.objects.bulk_create(warnings)

    if errors:
        translation.errors.all().delete()
        Error.objects.bulk_create(errors)


def checks_failed(checks, ignore_warnings):
    """
    Determine if the backend should block update of a translation because
    some of failed checks are critical e.g. compare-locales errors.

    :arg dict checks: dictionary with list of errors/warnings per library
    :arg bool ignore_warnings: removes warnings from failed checks
    """
    has_errors = any(p.endswith('Errors') for p in checks)

    return (not ignore_warnings and checks) or has_errors
