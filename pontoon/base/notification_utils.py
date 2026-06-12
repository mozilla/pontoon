from typing import TYPE_CHECKING, cast

from notifications.models import Notification

from django.conf import settings
from django.db.models import QuerySet
from django.urls import reverse

from pontoon.base.utils import format_datetime


if TYPE_CHECKING:
    from pontoon.base.models import Entity, Project, User


def user_notifications(user: "User", prefetch: bool = False) -> QuerySet[Notification]:
    qs = Notification.objects.filter(recipient=user)
    return qs.prefetch_related("actor", "target", "action_object") if prefetch else qs


def menu_notifications(user: "User", unread_count):
    """A list of notifications to display in the notifications menu."""
    count = settings.NOTIFICATIONS_MAX_COUNT

    if unread_count > count:
        count = unread_count

    return user_notifications(user, prefetch=True)[:count]


def unread_notifications_display(_, unread_count: int):
    """Textual representation of the unread notifications count."""
    return "9+" if unread_count > 9 else str(unread_count)


def is_subscribed_to_notification(user: "User", notification: Notification) -> bool:
    """
    Determines if the user has email subscription to the given notification.
    """
    if not notification.data:
        return False

    match notification.data.get("category"):
        case "direct_message":
            return True
        case "new_string":
            return user.profile.new_string_notifications_email
        case "project_deadline":
            return user.profile.project_deadline_notifications_email
        case "comment":
            return user.profile.comment_notifications_email
        case "unreviewed_suggestion":
            return user.profile.unreviewed_suggestion_notifications_email
        case "review":
            return user.profile.review_notifications_email
        case "new_contributor":
            return user.profile.new_contributor_notifications_email
        case _:
            return False


def serialized_notifications(user: "User"):
    """Serialized list of notifications to display in the notifications menu."""
    unread_count: int = user_notifications(user).unread().count()
    count: int = settings.NOTIFICATIONS_MAX_COUNT
    notifications = []

    if unread_count > count:
        count = unread_count

    for notification in user_notifications(user, prefetch=True)[:count]:
        actor = None
        is_comment = False

        if hasattr(notification.actor, "slug"):
            proj = cast("Project", notification.actor)
            if "new string" in notification.verb:
                new_strings_url = reverse(
                    "pontoon.translate.locale.agnostic",
                    kwargs={"slug": proj.slug, "part": "all-resources"},
                )
                # Link to the exact batch of added strings via the created_time
                # URL filter on Entity.date_created, falling back to all
                # missing/pretranslated strings for older notifications.
                created_time = (
                    notification.data.get("created_time") if notification.data else None
                )
                if created_time:
                    new_strings_url += f"?created_time={created_time}-{created_time}"
                else:
                    new_strings_url += "?status=missing,pretranslated"
                actor = {"anchor": proj.name, "url": new_strings_url}
            else:
                actor = {
                    "anchor": proj.name,
                    "url": reverse(
                        "pontoon.projects.project", kwargs={"slug": proj.slug}
                    ),
                }
        elif hasattr(notification.actor, "email"):
            user = cast("User", notification.actor)
            actor = {
                "anchor": user.first_name or user.email,
                "url": reverse(
                    "pontoon.contributors.contributor.username",
                    kwargs={"username": user.username},
                ),
            }

        target = None
        if notification.target:
            # New string or Manual notification
            if hasattr(notification.target, "slug"):
                proj = cast("Project", notification.target)
                target = {
                    "anchor": proj.name,
                    "url": reverse(
                        "pontoon.projects.project", kwargs={"slug": proj.slug}
                    ),
                }

            # Comment notifications
            elif hasattr(notification.target, "resource"):
                ent = cast("Entity", notification.target)
                is_comment = True
                target = {
                    "anchor": ent.resource.project.name,
                    "url": reverse(
                        "pontoon.translate",
                        kwargs={
                            "locale": notification.action_object.code,
                            "project": ent.resource.project.slug,
                            "resource": ent.resource.path,
                        },
                    )
                    + f"?string={ent.pk}",
                }

        notifications.append(
            {
                "id": notification.pk,
                "level": notification.level,
                "unread": notification.unread,
                "description": {
                    "content": notification.description,
                    "is_comment": is_comment,
                },
                "verb": notification.verb,
                "date": format_datetime(notification.timestamp, "full"),
                "date_iso": notification.timestamp.isoformat(),
                "actor": actor,
                "target": target,
            }
        )

    return {
        "has_unread": unread_count > 0,
        "notifications": notifications,
        "unread_count": unread_notifications_display(user, unread_count),
    }
