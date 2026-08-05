import pytest

from allauth.socialaccount.models import SocialAccount

from django.db.utils import IntegrityError

from pontoon.base.models.user import User
from pontoon.base.models.user_profile import UserProfile
from pontoon.base.user_utils import (
    avatar_url,
    fxa_avatar_url,
    get_pretranslation_authors,
    get_system_user,
    human_users,
    system_users,
    user_banner,
    user_locale_role,
    user_role,
)


@pytest.mark.django_db
def test_human_users(user_a, sync_user, gt_user, tm_user):
    users = human_users()
    assert user_a in users
    assert not any(user in users for user in (sync_user, gt_user, tm_user))


@pytest.mark.django_db
def test_system_users(user_a, sync_user, gt_user, tm_user):
    assert set(system_users()) == {sync_user, gt_user, tm_user}
    assert user_a not in system_users()

    # Filtered by role
    assert set(system_users(UserProfile.SystemUserRole.SYNC)) == {sync_user}

    # Bots without a role are still system users
    user_a.profile.system_user = True
    user_a.profile.save()
    assert user_a in system_users()
    assert user_a not in system_users(UserProfile.SystemUserRole.SYNC)


@pytest.mark.django_db
def test_system_user_role_is_unique(user_a, sync_user):
    """Two profiles can't share a role."""
    profile = user_a.profile
    profile.system_user = True
    profile.system_user_role = UserProfile.SystemUserRole.SYNC
    with pytest.raises(IntegrityError):
        profile.save()


@pytest.mark.django_db
def test_get_system_user(sync_user, gt_user, tm_user):
    assert get_system_user(UserProfile.SystemUserRole.SYNC) == sync_user
    assert get_system_user(UserProfile.SystemUserRole.GOOGLE_TRANSLATE) == gt_user
    assert get_system_user(UserProfile.SystemUserRole.TRANSLATION_MEMORY) == tm_user


@pytest.mark.django_db
def test_get_pretranslation_authors(sync_user, gt_user, tm_user):
    assert get_pretranslation_authors() == {"gt": gt_user, "tm": tm_user}


@pytest.mark.django_db
def test_get_pretranslation_authors_missing(gt_user, tm_user):
    """An incomplete set of authors is an error."""
    profile = gt_user.profile
    profile.system_user_role = None
    profile.save()

    with pytest.raises(User.DoesNotExist, match="pretranslation roles: gt"):
        get_pretranslation_authors()


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


@pytest.mark.django_db
def test_fxa_avatar_returns_none_for_unsaved_user():
    user = User(username="unsaved", email="unsaved@example.com")
    assert fxa_avatar_url(user) is None


@pytest.mark.django_db
def test_fxa_avatar_returns_url_from_db(user_a):
    SocialAccount.objects.create(
        user=user_a,
        provider="fxa",
        uid="1234",
        extra_data={"avatar": "https://profile.accounts.firefox.com/v1/avatar/abc"},
    )
    assert (
        fxa_avatar_url(user_a) == "https://profile.accounts.firefox.com/v1/avatar/abc"
    )


@pytest.mark.django_db
def test_fxa_avatar_returns_none_when_no_fxa_account(user_a):
    assert fxa_avatar_url(user_a) is None


@pytest.mark.django_db
def test_fxa_avatar_returns_none_when_fxa_has_no_avatar(user_a):
    SocialAccount.objects.create(
        user=user_a,
        provider="fxa",
        uid="1234",
        extra_data={},
    )
    assert fxa_avatar_url(user_a) is None


@pytest.mark.django_db
def test_fxa_avatar_uses_prefetched_accounts(user_a):
    account = SocialAccount(
        user=user_a,
        provider="fxa",
        uid="1234",
        extra_data={
            "avatar": "https://profile.accounts.firefox.com/v1/avatar/prefetched"
        },
    )
    user_a._prefetched_fxa_accounts = [account]
    assert (
        fxa_avatar_url(user_a)
        == "https://profile.accounts.firefox.com/v1/avatar/prefetched"
    )


@pytest.mark.django_db
def test_fxa_avatar_uses_prefetched_accounts_when_empty(user_a):
    user_a._prefetched_fxa_accounts = []
    assert fxa_avatar_url(user_a) is None
