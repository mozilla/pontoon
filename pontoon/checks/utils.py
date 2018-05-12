from pontoon.base.models import Translation
from pontoon.checks.models import (
    Warning,
    Error
)

def save_failed_checks(translation, checks):
    """

    """
    warnings = []
    errors = []
    for check_group, failed_checks in checks.items():
        library = (
            check_group
            .replace('Warnings', '')
            .replace('Errors', '')
        )
        severity_cls, messages_list = (Error, errors) if check_group.endswith('Errors') else (Warning, warnings)

        messages_list.extend([
            severity_cls(
                library=library,
                message=failed_check,
                translation=translation,
            ) for failed_check in failed_checks
        ])

    Warning.objects.bulk_create(warnings)
    Error.objects.bulk_create(errors)
