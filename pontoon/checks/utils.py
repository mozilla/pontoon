from pontoon.checks import DB_LIBRARIES


def bulk_run_checks(translations):
    """
    Run checks on a list of translations

    *Important*
    To avoid performance problems, translations have to prefetch entities and locales objects.
    """
    from pontoon.checks.libraries import run_checks
    from pontoon.checks.models import Warning, Error

    warnings, errors = [], []
    if not translations:
        return

    for translation in translations:
        warnings_, errors_ = get_failed_checks_db_objects(
            translation,
            run_checks(
                translation.entity,
                translation.locale.code,
                translation.entity.string,
                translation.string,
                use_tt_checks=False,
            ),
        )
        warnings.extend(warnings_)
        errors.extend(errors_)

    # Remove old warnings and errors
    Warning.objects.filter(translation__pk__in=[t.pk for t in translations]).delete()
    Error.objects.filter(translation__pk__in=[t.pk for t in translations]).delete()

    # Insert new warnings and errors
    Warning.objects.bulk_create(warnings)
    Error.objects.bulk_create(errors)

    return warnings, errors


def get_failed_checks_db_objects(translation, failed_checks):
    """
    Return model instances of Warnings and Errors
    :arg Translation translation: instance of translation
    :arg dict failed_checks: dictionary with failed checks
    """
    from pontoon.checks.models import Warning, Error

    warnings = []
    errors = []

    for check_group, messages in failed_checks.items():
        library = check_group.replace("Warnings", "").replace("Errors", "")
        if library not in DB_LIBRARIES:
            continue

        if check_group.endswith("Errors"):
            severity_cls, messages_list = Error, errors
        else:
            severity_cls, messages_list = Warning, warnings

        messages_list.extend(
            [
                severity_cls(library=library, message=message, translation=translation,)
                for message in messages
            ]
        )

    return warnings, errors


def save_failed_checks(translation, failed_checks):
    """
    Save all failed checks to Database
    :arg Translation translation: instance of translation
    :arg dict failed_checks: dictionary with failed checks
    """
    warnings, errors = get_failed_checks_db_objects(translation, failed_checks)

    translation.warnings.all().delete()
    translation.errors.all().delete()

    translation.warnings.bulk_create(warnings)
    translation.errors.bulk_create(errors)


def are_blocking_checks(checks, ignore_warnings):
    """
    Return True if checks are errors or unignored warnings.

    :arg dict checks: dictionary with a list of errors/warnings per library
    :arg bool ignore_warnings: ignores failed checks of type warning
    """
    has_errors = any(p.endswith("Errors") for p in checks)

    return (not ignore_warnings and checks) or has_errors
