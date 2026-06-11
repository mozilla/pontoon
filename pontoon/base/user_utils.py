from hashlib import md5
from typing import TYPE_CHECKING, Any, Collection
from urllib.parse import quote, urlencode

from allauth.socialaccount.models import SocialAccount
from dateutil.relativedelta import relativedelta
from guardian.shortcuts import get_objects_for_user

from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone


if TYPE_CHECKING:
    from pontoon.base.models import Locale, Project, User
else:
    from django.contrib.auth.models import User


def is_system_user(user: User) -> bool:
    return user.pk is None or user.profile.system_user


def avatar_url(user: User, size: int = 88) -> str:
    fxa_account = SocialAccount.objects.filter(user=user, provider="fxa").first()
    if fxa_account:
        fxa_avatar = fxa_account.extra_data.get("avatar")
        if fxa_avatar:
            return fxa_avatar

    email = md5(user.email.lower().encode("utf-8")).hexdigest()

    name = quote(user.display_name)
    background = "333941"
    color = "FFFFFF"
    url = f"https://ui-avatars.com/api/{name}/{size}/{background}/{color}"
    data = urlencode({"s": str(size), "d": url})

    return f"//www.gravatar.com/avatar/{email}?{data}"


def profile_url(user: User) -> str:
    return reverse(
        "pontoon.contributors.contributor.username", kwargs={"username": user.username}
    )


def user_serialize(user: User):
    """Serialize Project contact"""

    return {
        "avatar": avatar_url(user),
        "name": user.name_or_email,
        "url": profile_url(user),
    }


def translator_for_locales(user: User) -> list["Locale"]:
    """A list of locales, in which the user is assigned Translator permissions.

    Only includes explicitly assigned locales for superusers.
    """
    return [
        locale
        for group in user.groups.all()
        if (locale := group.translated_locales.first())
    ]


def manager_for_locales(user: User) -> list["Locale"]:
    """A list of locales, in which the user is assigned Manager permissions.

    Only includes explicitly assigned locales for superusers.
    """
    return [
        locale
        for group in user.groups.all()
        if (locale := group.managed_locales.first())
    ]


def can_translate_locales(user: User) -> QuerySet[Any]:
    """A list of locale codes the user has permission to translate.

    Includes all locales for superusers.
    """
    return get_objects_for_user(
        user, "base.can_translate_locale", accept_global_perms=False
    ).values_list("code", flat=True)


def can_manage_locales(user: User) -> QuerySet[Any]:
    """A list of locale codes the user has permission to manage.

    Includes all locales for superusers.
    """
    return get_objects_for_user(
        user, "base.can_manage_locale", accept_global_perms=False
    ).values_list("code", flat=True)


def translated_projects(user: User) -> dict[str, bool]:
    """
    Returns a map of permission for every project-locale
    """
    from pontoon.base.models.project_locale import ProjectLocale

    user_project_locales: Collection[int] = (
        get_objects_for_user(
            user, "base.can_translate_project_locale", accept_global_perms=False
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


def user_role(user: User, managers=None, translators=None) -> str:
    """
    Prefetched managers and translators dicts help reduce the number of queries
    on pages that contain a lot of users, like the Top Contributors page.
    """
    if user.is_superuser:
        return "Admin"

    if is_system_user(user):
        return "System User"

    if managers is not None:
        if user in managers:
            return "Manager for " + ", ".join(managers[user])
    elif manager_for_locales := can_manage_locales(user):
        return "Manager for " + ", ".join(manager_for_locales)

    if translators is not None:
        if user in translators:
            return "Translator for " + ", ".join(translators[user])
    elif translator_for_locales := can_translate_locales(user):
        return "Translator for " + ", ".join(translator_for_locales)

    return "Contributor"


def user_locale_role(user: User, locale: "Locale") -> str:
    if user in locale.managers_group.user_set.all():
        return "Manager"
    if user in locale.translators_group.user_set.all():
        return "Translator"
    if user.is_superuser:
        return "Admin"
    if is_system_user(user):
        return "System User"
    else:
        return "Contributor"


def user_banner(
    user: User, locale: "Locale", project_contact: User | None
) -> tuple[str, str]:
    if is_system_user(user):
        return ("", "")
    if user in locale.managers_group.user_set.all():
        return ("MNGR", "Team Manager")
    if user in locale.translators_group.user_set.all():
        return ("TRNSL", "Translator")
    if project_contact and user.pk == project_contact.pk:
        return ("PM", "Project Manager")
    if user.is_superuser:
        return ("ADMIN", "Admin")
    if user.date_joined >= timezone.now() - relativedelta(months=3):
        return ("NEW", "New User")
    return ("", "")


def can_translate(user: User, project: "Project", locale: "Locale") -> bool:
    """Check if user has suitable permissions to translate in given locale or project/locale."""
    from pontoon.base.models.project_locale import ProjectLocale

    # Locale managers can translate all projects
    if user.has_perm("base.can_manage_locale", locale):
        return True

    project_locale = ProjectLocale.objects.get(project=project, locale=locale)
    if project_locale.has_custom_translators:
        return user.has_perm("base.can_translate_project_locale", project_locale)

    return user.has_perm("base.can_translate_locale", locale)
