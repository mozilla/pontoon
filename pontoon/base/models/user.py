from datetime import timedelta
from hashlib import md5
from urllib.parse import quote, urlencode

from dateutil.relativedelta import relativedelta
from guardian.shortcuts import get_objects_for_user

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Exists, OuterRef, Q
from django.urls import reverse
from django.utils import timezone

from pontoon.actionlog.models import ActionLog


@property
def user_profile_url(self):
    return reverse(
        "pontoon.contributors.contributor.username", kwargs={"username": self.username}
    )


def user_gravatar_url(self, size):
    email = md5(self.email.lower().encode("utf-8")).hexdigest()
    data = {
        "s": str(size),
        "d": "https://ui-avatars.com/api/{name}/{size}/{background}/{color}".format(
            name=quote(self.display_name),
            size=size,
            background="333941",
            color="FFFFFF",
        ),
    }

    return "//www.gravatar.com/avatar/{email}?{data}".format(
        email=email, data=urlencode(data)
    )


@property
def user_gravatar_url_small(self):
    return user_gravatar_url(self, 88)


@property
def user_name_or_email(self):
    return self.first_name or self.email


@property
def user_contact_email(self):
    return self.profile.contact_email or self.email


@property
def user_display_name(self):
    return self.first_name or self.email.split("@")[0]


@property
def user_display_name_and_email(self):
    name = self.display_name
    return f"{name} <{self.email}>"


@classmethod
def user_display_name_or_blank(cls, user):
    """Shorcut function that displays user info if user isn't none."""
    return user.name_or_email if user else ""


@property
def user_translator_for_locales(self):
    """A list of locales, in which the user is assigned Translator permissions.

    Only includes explicitly assigned locales for superusers.
    """
    locales = []

    for group in self.groups.all():
        locale = group.translated_locales.first()
        if locale:
            locales.append(locale)

    return locales


@property
def user_manager_for_locales(self):
    """A list of locales, in which the user is assigned Manager permissions.

    Only includes explicitly assigned locales for superusers.
    """
    locales = []

    for group in self.groups.all():
        locale = group.managed_locales.first()
        if locale:
            locales.append(locale)

    return locales


@property
def user_can_translate_locales(self):
    """A list of locale codes the user has permission to translate.

    Includes all locales for superusers.
    """
    return get_objects_for_user(
        self, "base.can_translate_locale", accept_global_perms=False
    )


@property
def user_can_manage_locales(self):
    """A list of locale codes the user has permission to manage.

    Includes all locales for superusers.
    """
    return get_objects_for_user(
        self, "base.can_manage_locale", accept_global_perms=False
    )


@property
def user_translated_projects(self):
    """
    Returns a map of permission for every user
    :param self:
    :return:
    """
    from pontoon.base.models.project_locale import ProjectLocale

    user_project_locales = (
        get_objects_for_user(
            self, "base.can_translate_project_locale", accept_global_perms=False
        )
    ).values_list("pk", flat=True)

    project_locales = ProjectLocale.objects.filter(
        has_custom_translators=True
    ).values_list("pk", "locale__code", "project__slug")
    permission_map = {
        f"{locale}-{project}": (pk in user_project_locales)
        for pk, locale, project in project_locales
    }
    return permission_map


def user_role(self, managers=None, translators=None):
    """
    Prefetched managers and translators dicts help reduce the number of queries
    on pages that contain a lot of users, like the Top Contributors page.
    """
    if self.is_superuser:
        return "Admin"

    if self.pk is None or self.profile.system_user:
        return "System User"

    if managers is not None:
        if self in managers:
            return "Manager for " + ", ".join(managers[self])
    else:
        if self.can_manage_locales:
            return "Manager for " + ", ".join(
                self.can_manage_locales.values_list("code", flat=True)
            )

    if translators is not None:
        if self in translators:
            return "Translator for " + ", ".join(translators[self])
    else:
        if self.can_translate_locales:
            return "Translator for " + ", ".join(
                self.can_translate_locales.values_list("code", flat=True)
            )

    return "Contributor"


def user_locale_role(self, locale):
    if self in locale.managers_group.user_set.all():
        return "Manager"
    if self in locale.translators_group.user_set.all():
        return "Translator"
    if self.is_superuser:
        return "Admin"
    if self.pk is None or self.profile.system_user:
        return "System User"
    else:
        return "Contributor"


def user_status(self, locale, project_contact):
    if self.pk is None or self.profile.system_user:
        return ("", "")
    if self in locale.managers_group.user_set.all():
        return ("MNGR", "Team Manager")
    if self in locale.translators_group.user_set.all():
        return ("TRNSL", "Translator")
    if project_contact and self.pk == project_contact.pk:
        return ("PM", "Project Manager")
    if self.is_superuser:
        return ("ADMIN", "Admin")
    if self.date_joined >= timezone.now() - relativedelta(months=3):
        return ("NEW", "New User")
    return ("", "")


@property
def contributed_translations(self):
    """Contributions provided by user."""
    return self.translation_set.all()


@property
def has_approved_translations(self):
    """Return True if the user has approved translations."""
    return self.translation_set.filter(approved=True).exists()


@property
def badges_translation_count(self):
    """Contributions provided by user that count towards their badges."""
    return self.actions.filter(
        action_type="translation:created",
        created_at__gte=settings.BADGES_START_DATE,
    ).count()


@property
def badges_review_count(self):
    """Translation reviews provided by user that count towards their badges."""
    # Exclude auto-rejections caused by creating a new translation or approving an existing one
    closely_preceded_action = ActionLog.objects.filter(
        performed_by=OuterRef("performed_by"),
        action_type__in=["translation:created", "translation:approved"],
        created_at__gt=OuterRef("created_at"),
        created_at__lte=OuterRef("created_at") + timedelta(milliseconds=100),
    )

    return self.actions.filter(
        Q(action_type="translation:approved")
        | Q(
            ~Exists(closely_preceded_action),
            action_type="translation:rejected",
        ),
        created_at__gte=settings.BADGES_START_DATE,
    ).count()


@property
def badges_promotion_count(self):
    """Role promotions performed by user that count towards their badges"""
    added_entries = self.changed_permissions_log.filter(
        action_type="added",
        created_at__gte=settings.BADGES_START_DATE,
    )

    # Check if user was demoted from Manager to Translator.
    # In this case, it doesn't count as a promotion.
    #
    # TODO:
    # This code is the only consumer of the PermissionChangelog model, so we should
    # refactor to simplify how promotions are retrieved. (see #2195)
    return (
        added_entries.exclude(
            Exists(
                self.changed_permissions_log.filter(
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


@property
def top_contributed_locale(self):
    """Locale the user has made the most contributions to."""
    try:
        return (
            self.translation_set.values("locale__code")
            .annotate(total=Count("locale__code"))
            .distinct()
            .order_by("-total")
            .first()["locale__code"]
        )
    except TypeError:
        # This error is raised if `top_contribution` is null. That happens if the user
        # has never contributed to any locales.
        return None


def can_translate(self, locale, project):
    """Check if user has suitable permissions to translate in given locale or project/locale."""
    from pontoon.base.models.project_locale import ProjectLocale

    # Locale managers can translate all projects
    if locale in self.can_manage_locales:
        return True

    project_locale = ProjectLocale.objects.get(project=project, locale=locale)
    if project_locale.has_custom_translators:
        return self.has_perm("base.can_translate_project_locale", project_locale)

    return self.has_perm("base.can_translate_locale", locale)


def is_new_contributor(self, locale):
    """Return True if the user hasn't made contributions to the locale yet."""
    return (
        not self.translation_set.filter(locale=locale)
        .exclude(entity__resource__project__system_project=True)
        .exists()
    )


@property
def notification_list(self):
    """A list of notifications to display in the notifications menu."""
    notifications = self.notifications.prefetch_related(
        "actor", "target", "action_object"
    )

    # In order to prefetch Resource and Project data for Entities, we need to split the
    # QuerySet into two parts: one for comment notifications, which store Entity objects
    # into the Notification.target field, and one for other notifications.
    comment_query = {
        "target_content_type": ContentType.objects.get(app_label="base", model="entity")
    }
    comment_notifications = notifications.filter(**comment_query).prefetch_related(
        "target__resource__project"
    )
    other_notifications = notifications.exclude(**comment_query)
    notifications = list(comment_notifications) + list(other_notifications)

    notifications.sort(key=lambda x: x.timestamp, reverse=True)

    return notifications


def menu_notifications(self, unread_count):
    """A list of notifications to display in the notifications menu."""
    count = settings.NOTIFICATIONS_MAX_COUNT

    if unread_count > count:
        count = unread_count

    return self.notifications.prefetch_related("actor", "target", "action_object")[
        :count
    ]


def unread_notifications_display(self, unread_count):
    """Textual representation of the unread notifications count."""
    if unread_count > 9:
        return "9+"

    return unread_count


@property
def serialized_notifications(self):
    """Serialized list of notifications to display in the notifications menu."""
    unread_count = self.notifications.unread().count()
    count = settings.NOTIFICATIONS_MAX_COUNT
    notifications = []

    if unread_count > count:
        count = unread_count

    for notification in self.notifications.prefetch_related(
        "actor", "target", "action_object"
    )[:count]:
        actor = None
        is_comment = False

        if hasattr(notification.actor, "slug"):
            if "new string" in notification.verb:
                actor = {
                    "anchor": notification.actor.name,
                    "url": reverse(
                        "pontoon.translate.locale.agnostic",
                        kwargs={
                            "slug": notification.actor.slug,
                            "part": "all-resources",
                        },
                    )
                    + "?status=missing,pretranslated",
                }
            else:
                actor = {
                    "anchor": notification.actor.name,
                    "url": reverse(
                        "pontoon.projects.project",
                        kwargs={"slug": notification.actor.slug},
                    ),
                }
        elif hasattr(notification.actor, "email"):
            actor = {
                "anchor": notification.actor.name_or_email,
                "url": reverse(
                    "pontoon.contributors.contributor.username",
                    kwargs={"username": notification.actor.username},
                ),
            }

        target = None
        if notification.target:
            t = notification.target
            # New string or Manual notification
            if hasattr(t, "slug"):
                target = {
                    "anchor": t.name,
                    "url": reverse(
                        "pontoon.projects.project",
                        kwargs={"slug": t.slug},
                    ),
                }

            # Comment notifications
            elif hasattr(t, "resource"):
                is_comment = True
                target = {
                    "anchor": t.resource.project.name,
                    "url": reverse(
                        "pontoon.translate",
                        kwargs={
                            "locale": notification.action_object.code,
                            "project": t.resource.project.slug,
                            "resource": t.resource.path,
                        },
                    )
                    + f"?string={t.pk}",
                }

        notifications.append(
            {
                "id": notification.id,
                "level": notification.level,
                "unread": notification.unread,
                "description": {
                    "content": notification.description,
                    "is_comment": is_comment,
                },
                "verb": notification.verb,
                "date": notification.timestamp.strftime("%b %d, %Y %H:%M"),
                "date_iso": notification.timestamp.isoformat(),
                "actor": actor,
                "target": target,
            }
        )

    return {
        "has_unread": unread_count > 0,
        "notifications": notifications,
        "unread_count": str(self.unread_notifications_display(unread_count)),
    }


def is_subscribed_to_notification(self, notification):
    """
    Determines if the user has email subscription to the given notification.
    """
    profile = self.profile
    category = notification.data.get("category") if notification.data else None

    CATEGORY_TO_FIELD = {
        "new_string": profile.new_string_notifications_email,
        "project_deadline": profile.project_deadline_notifications_email,
        "comment": profile.comment_notifications_email,
        "unreviewed_suggestion": profile.unreviewed_suggestion_notifications_email,
        "review": profile.review_notifications_email,
        "new_contributor": profile.new_contributor_notifications_email,
    }

    return CATEGORY_TO_FIELD.get(category, False)


def user_serialize(self):
    """Serialize Project contact"""

    return {
        "avatar": self.gravatar_url_small,
        "name": self.name_or_email,
        "url": self.profile_url,
    }


@property
def latest_action(self):
    """
    Return the date of the latest user activity (translation submission or review).
    """
    try:
        return ActionLog.objects.filter(
            performed_by=self,
            action_type__startswith="translation:",
        ).latest("created_at")
    except ActionLog.DoesNotExist:
        return None


User.add_to_class("profile_url", user_profile_url)
User.add_to_class("gravatar_url", user_gravatar_url)
User.add_to_class("gravatar_url_small", user_gravatar_url_small)
User.add_to_class("name_or_email", user_name_or_email)
User.add_to_class("contact_email", user_contact_email)
User.add_to_class("display_name", user_display_name)
User.add_to_class("display_name_and_email", user_display_name_and_email)
User.add_to_class("display_name_or_blank", user_display_name_or_blank)
User.add_to_class("translator_for_locales", user_translator_for_locales)
User.add_to_class("manager_for_locales", user_manager_for_locales)
User.add_to_class("can_translate_locales", user_can_translate_locales)
User.add_to_class("can_manage_locales", user_can_manage_locales)
User.add_to_class("translated_projects", user_translated_projects)
User.add_to_class("role", user_role)
User.add_to_class("locale_role", user_locale_role)
User.add_to_class("status", user_status)
User.add_to_class("contributed_translations", contributed_translations)
User.add_to_class("badges_translation_count", badges_translation_count)
User.add_to_class("badges_review_count", badges_review_count)
User.add_to_class("badges_promotion_count", badges_promotion_count)
User.add_to_class("has_approved_translations", has_approved_translations)
User.add_to_class("top_contributed_locale", top_contributed_locale)
User.add_to_class("can_translate", can_translate)
User.add_to_class("is_new_contributor", is_new_contributor)
User.add_to_class("notification_list", notification_list)
User.add_to_class("menu_notifications", menu_notifications)
User.add_to_class("unread_notifications_display", unread_notifications_display)
User.add_to_class("serialized_notifications", serialized_notifications)
User.add_to_class("is_subscribed_to_notification", is_subscribed_to_notification)
User.add_to_class("serialize", user_serialize)
User.add_to_class("latest_action", latest_action)
