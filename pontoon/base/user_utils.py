from collections.abc import Collection
from hashlib import md5
from typing import TYPE_CHECKING, Any
from urllib.parse import quote, urlencode

from dateutil.relativedelta import relativedelta
from guardian.shortcuts import get_objects_for_user

from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone


if TYPE_CHECKING:
    from pontoon.base.models import Locale, Project, User
    from pontoon.base.models.user_profile import UserProfile

    SystemUserRole = UserProfile.SystemUserRole
else:
    from django.contrib.auth.models import User


def is_system_user(user: User) -> bool:
    return user.pk is None or user.profile.system_user


def human_users() -> QuerySet[Any]:
    """All users that are not system users."""
    return User.objects.filter(profile__system_user=False)


def system_users(role: "SystemUserRole | None" = None) -> QuerySet[Any]:
    """All system users, optionally limited to those serving a specific role."""
    users = User.objects.filter(profile__system_user=True)
    return users.filter(profile__system_user_role=role) if role else users


def get_system_user(role: "SystemUserRole") -> User:
    """The system user serving the given role."""
    return system_users(role).get()


def get_pretranslation_authors() -> dict[str, User]:
    """System users used as authors of pretranslations, keyed by role.

    Raises User.DoesNotExist if any of them is missing. Callers use the authors
    both to attribute new pretranslations and to recognize existing ones, and
    neither works with an incomplete set.
    """
    from pontoon.base.models.user_profile import UserProfile

    roles = [
        UserProfile.SystemUserRole.TRANSLATION_MEMORY,
        UserProfile.SystemUserRole.GOOGLE_TRANSLATE,
    ]
    authors = {
        user.profile.system_user_role: user
        for user in system_users()
        .filter(profile__system_user_role__in=roles)
        .select_related("profile")
    }
    if missing := set(roles) - authors.keys():
        raise User.DoesNotExist(
            f"No system user found for pretranslation roles: {', '.join(sorted(missing))}"
        )
    return authors


def fxa_avatar_url(user: User) -> str | None:
    if user.pk is None:
        return None

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


def avatar_url(user: User, size: int = 88) -> str:

    if fxa_avatar := fxa_avatar_url(user):
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
