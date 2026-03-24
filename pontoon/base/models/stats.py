from django.db.models import Count, Q


def aggregate_translation_stats(queryset) -> dict[str, int]:
    """
    Aggregate translation stats for a given Translation queryset.

    :return: a dictionary with approved, pretranslated, errors, warnings,
             and unreviewed counts.
    """
    stats = queryset.aggregate(
        approved_count=Count(
            "pk",
            filter=Q(approved=True, errors__isnull=True, warnings__isnull=True),
        ),
        pretranslated_count=Count(
            "pk",
            filter=Q(pretranslated=True, errors__isnull=True, warnings__isnull=True),
        ),
        errors_count=Count(
            "pk",
            distinct=True,
            filter=Q(
                Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                & Q(errors__isnull=False)
            ),
        ),
        warnings_count=Count(
            "pk",
            distinct=True,
            filter=Q(
                Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                & Q(warnings__isnull=False)
            ),
        ),
        unreviewed_count=Count(
            "pk",
            filter=Q(approved=False, rejected=False, pretranslated=False, fuzzy=False),
        ),
    )
    return {
        "approved": stats["approved_count"],
        "pretranslated": stats["pretranslated_count"],
        "errors": stats["errors_count"],
        "warnings": stats["warnings_count"],
        "unreviewed": stats["unreviewed_count"],
    }
