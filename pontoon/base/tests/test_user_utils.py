import pytest

from allauth.socialaccount.models import SocialAccount

from pontoon.base.models.user import User
from pontoon.base.user_utils import avatar_url, user_banner, user_locale_role, user_role


@pytest.mark.django_db
def test_user_role(user_a, user_b, user_c, locale_a):
    # Default role
    assert user_role(user_a) == "Contributor"

    # Superuser
    user_a.is_superuser = True
    assert user_role(user_a) == "Admin"

    # Fake user object
    imported = User(username="Imported")
    assert user_role(imported) == "System User"

    # System user
    user_b.profile.system_user = True
    assert user_role(user_b) == "System User"

    # Translator
    translators = {user_c: {locale_a.code}}
    assert (
        user_role(user_c, translators=translators) == f"Translator for {locale_a.code}"
    )

    # Manager
    managers = {user_c: {locale_a.code}}
    assert user_role(user_c, managers=managers) == f"Manager for {locale_a.code}"


@pytest.mark.django_db
def test_user_locale_role(user_a, user_b, user_c, locale_a):
    # Default role
    assert user_locale_role(user_a, locale_a) == "Contributor"

    # Superuser
    user_a.is_superuser = True
    assert user_locale_role(user_a, locale_a) == "Admin"

    # Fake user object
    imported = User(username="Imported")
    assert user_locale_role(imported, locale_a) == "System User"

    # System user
    user_b.profile.system_user = True
    assert user_locale_role(user_b, locale_a) == "System User"

    # Translator
    locale_a.translators_group.user_set.add(user_c)
    assert user_locale_role(user_c, locale_a) == "Translator"

    # Manager
    locale_a.managers_group.user_set.add(user_c)
    assert user_locale_role(user_c, locale_a) == "Manager"

    # Admin and Manager
    locale_a.managers_group.user_set.add(user_a)
    assert user_locale_role(user_a, locale_a) == "Manager"


@pytest.mark.django_db
def test_user_banner(user_a, user_b, user_c, user_d, gt_user, locale_a, project_a):
    project_contact = user_d

    # New User
    assert user_banner(user_a, locale_a, project_contact)[1] == "New User"

    # Fake user object
    imported = User(username="Imported")
    assert user_banner(imported, locale_a, project_contact)[1] == ""

    # Admin
    user_a.is_superuser = True
    assert user_banner(user_a, locale_a, project_contact)[1] == "Admin"

    # Manager
    locale_a.managers_group.user_set.add(user_b)
    assert user_banner(user_b, locale_a, project_contact)[1] == "Team Manager"

    # Translator
    locale_a.translators_group.user_set.add(user_c)
    assert user_banner(user_c, locale_a, project_contact)[1] == "Translator"

    # PM
    assert user_banner(user_d, locale_a, project_contact)[1] == "Project Manager"

    # System user (Google Translate)
    project_contact = gt_user
    assert user_banner(gt_user, locale_a, project_contact)[1] == ""


@pytest.mark.django_db
def test_gravatar_url_returns_fxa_avatar_when_linked(user_a):
    SocialAccount.objects.create(
        user=user_a,
        provider="fxa",
        uid="1234",
        extra_data={"avatar": "https://profile.accounts.firefox.com/v1/avatar/abc"},
    )
    assert avatar_url(user_a) == "https://profile.accounts.firefox.com/v1/avatar/abc"


@pytest.mark.django_db
def test_gravatar_url_falls_back_to_gravatar_when_no_fxa(user_a):
    url = avatar_url(user_a)
    assert "gravatar.com/avatar/" in url


@pytest.mark.django_db
def test_gravatar_url_falls_back_to_gravatar_when_fxa_has_no_avatar(user_a):
    SocialAccount.objects.create(
        user=user_a,
        provider="fxa",
        uid="1234",
        extra_data={},
    )
    url = avatar_url(user_a)
    assert "gravatar.com/avatar/" in url
