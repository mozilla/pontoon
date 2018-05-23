from pontoon.checks.models import Warning, Error


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


def are_blocking_checks(checks, ignore_warnings):
    """
    Return True if checks are errors or unignored warnings.

    :arg dict checks: dictionary with a list of errors/warnings per library
    :arg bool ignore_warnings: ignores failed checks of type warning
    """
    has_errors = any(p.endswith('Errors') for p in checks)

    return (not ignore_warnings and checks) or has_errors
