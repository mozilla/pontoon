from pontoon.base.models import Translation
from pontoon.checks.models import (
    Warning,
    Error
)

def save_failed_checks(translation, messages):
    """

    """
    warnings = []
    errors = []
    for check_group, messages in messages.items():
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
        translation.warnings.clear()
        Warning.objects.bulk_create(warnings)

    if errors:
        translation.errors.clear()
        Error.objects.bulk_create(errors)
