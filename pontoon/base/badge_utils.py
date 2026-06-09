from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef

from pontoon.actionlog.models import ActionLog
from pontoon.base.models.permission_changelog import PermissionChangelog


def badges_translation_count(user: User) -> int:
    """Contributions provided by user that count towards their badges."""
    return ActionLog.objects.filter(
        performed_by=user,
        action_type="translation:created",
        created_at__gte=settings.BADGES_START_DATE,
    ).count()


def badges_review_count(user: User) -> int:
    """Translation reviews provided by user that count towards their badges."""
    return ActionLog.objects.filter(
        performed_by=user,
        action_type__in={"translation:approved", "translation:rejected"},
        created_at__gte=settings.BADGES_START_DATE,
        is_implicit_action=False,
    ).count()


def badges_promotion_count(user: User) -> int:
    """Role promotions performed by user that count towards their badges"""

    # Check if user was demoted from Manager to Translator.
    # In this case, it doesn't count as a promotion.
    #
    # TODO:
    # This code is the only consumer of the PermissionChangelog model, so we should
    # refactor to simplify how promotions are retrieved. (see #2195)
    return (
        PermissionChangelog.objects.filter(
            performed_by=user,
            action_type="added",
            created_at__gte=settings.BADGES_START_DATE,
        )
        .exclude(
            Exists(
                PermissionChangelog.objects.filter(performed_by=user).filter(
                    performed_by=OuterRef("performed_by"),
                    performed_on=OuterRef("performed_on"),
                    action_type="removed",
                    created_at__gt=OuterRef("created_at"),
                    created_at__lte=OuterRef("created_at") + timedelta(milliseconds=10),
                )
            )
        )
        .order_by("performed_on", "group")
        # Only count promotion of each user to the same group once
        .distinct("performed_on", "group")
        .count()
    )


def badges_translation_level(user: User) -> int:
    thresholds = settings.BADGES_TRANSLATION_THRESHOLDS
    count = badges_translation_count(user)
    for level in range(len(thresholds) - 1):
        if thresholds[level] <= count < thresholds[level + 1]:
            return level + 1
    return 0


def badges_review_level(user: User) -> int:
    thresholds = settings.BADGES_REVIEW_THRESHOLDS
    count = badges_review_count(user)
    for level in range(len(thresholds) - 1):
        if thresholds[level] <= count < thresholds[level + 1]:
            return level + 1
    return 0
