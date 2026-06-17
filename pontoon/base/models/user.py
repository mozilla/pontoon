from typing import TYPE_CHECKING

from django.contrib.auth.models import User as AuthUser

from pontoon.actionlog.models import ActionLog
from pontoon.base.notification_utils import (
    is_subscribed_to_notification,
    menu_notifications,
    unread_notifications_display,
)
from pontoon.base.user_utils import (
    avatar_url,
    can_translate_locales,
    manager_for_locales,
    translator_for_locales,
)


if TYPE_CHECKING:
    from notifications.models import Notification

    from django.db.models import QuerySet

    from pontoon.base.models import UserProfile
    from pontoon.base.models.project import ProjectQuerySet
    from pontoon.base.models.translation import TranslationQuerySet
    from pontoon.base.models.user_banlog import UserBanLog

    class User(AuthUser):
        """
        A Pontoon user.

        We attach some properties and methods on the base User model, using `Model.addtoClass()`.
        This monkeypatching is partly due to historical reasons,
        and partly to ensure that the values are available during template formatting.

        You probably should not add more monkeypatching here,
        unless you can come up with a really good excuse.
        """

        name_or_email: str
        contact_email: str
        display_name: str
        display_name_and_email: str

        ban_log: QuerySet[UserBanLog]
        contact_for: ProjectQuerySet
        notifications: QuerySet[Notification]
        profile: UserProfile
        translation_set: TranslationQuerySet
else:
    User = AuthUser


@property
def name_or_email(user: User) -> str:
    return user.first_name or user.email


@property
def contact_email(user: User) -> str:
    return user.profile.contact_email or user.email


@property
def display_name(user: User) -> str:
    return user.first_name or user.email.split("@")[0]


@property
def display_name_and_email(user: User) -> str:
    name = user.display_name
    return f"{name} <{user.email}>"


def fxa_avatar(user: User) -> str | None:
    if user.pk is None:
        return

    if hasattr(user, "_prefetched_fxa_accounts") and isinstance(
        user._prefetched_fxa_accounts, list
    ):
        return (
            user._prefetched_fxa_accounts[0].extra_data.get("avatar")
            if user._prefetched_fxa_accounts
            else None
        )

    fxa = user.socialaccount_set.filter(provider="fxa").first()
    return fxa.extra_data.get("avatar") if fxa else None


def latest_action(user: User) -> ActionLog | None:
    """
    Return the date of the latest user activity (translation submission or review).
    """
    try:
        return ActionLog.objects.filter(
            performed_by=user,
            action_type__startswith="translation:",
        ).latest("created_at")
    except ActionLog.DoesNotExist:
        return None


AuthUser.add_to_class("name_or_email", name_or_email)
AuthUser.add_to_class("contact_email", contact_email)
AuthUser.add_to_class("display_name", display_name)
AuthUser.add_to_class("display_name_and_email", display_name_and_email)
AuthUser.add_to_class("latest_action", latest_action)

AuthUser.add_to_class("avatar_url", avatar_url)
AuthUser.add_to_class("fxa_avatar", fxa_avatar)
AuthUser.add_to_class("translator_for_locales", translator_for_locales)
AuthUser.add_to_class("manager_for_locales", manager_for_locales)
AuthUser.add_to_class("can_translate_locales", can_translate_locales)

AuthUser.add_to_class("menu_notifications", menu_notifications)
AuthUser.add_to_class("unread_notifications_display", unread_notifications_display)
AuthUser.add_to_class("is_subscribed_to_notification", is_subscribed_to_notification)
