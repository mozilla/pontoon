from pontoon.checks import DB_EXCLUDE_LIBRARIES
from pontoon.checks.models import Warning, Error


def get_failed_checks_db_objects(translation, failed_checks, excluded=None):
    """
    Return model instances of Warnings and Errors
    :arg Translation translation: instance of translation
    :arg dict failed_checks: dictionary with failed checks
    :arg tuple exclude_libraries:
    """
    warnings = []
    errors = []

    for check_group, messages in failed_checks.items():
        library = (
            check_group
            .replace('Warnings', '')
            .replace('Errors', '')
        )
        if library in DB_EXCLUDE_LIBRARIES:
            continue

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
    return warnings, errors


def save_failed_checks(translation, failed_checks):
    """
    Save all failed checks to Database
    :arg Translation translation: instance of translation
    :arg dict failed_checks: dictionary with failed checks
    """
    warnings, errors = get_failed_checks_db_objects(translation, failed_checks)

    Warning.objects.bulk_create(warnings)
    Error.objects.bulk_create(errors)


def are_blocking_checks(checks, ignore_warnings):
    """
    Return True if checks are errors or unignored warnings.

    :arg dict checks: dictionary with a list of errors/warnings per library
    :arg bool ignore_warnings: ignores failed checks of type warning
    """
    has_errors = any(p.endswith('Errors') for p in checks)

    return (not ignore_warnings and checks) or has_errors
