from collections import defaultdict

import pytest

from django.contrib.auth.models import User


@pytest.mark.django_db
def test_user_role(user_a, user_b, user_c, locale_a):
    # Default role
    assert user_a.role() == "Contributor"

    # Superuser
    user_a.is_superuser = True
    assert user_a.role() == "Admin"

    # Fake user object
    imported = User(username="Imported")
    assert imported.role() == "System User"

    # System user
    user_b.profile.system_user = True
    assert user_b.role() == "System User"

    # Translator
    translators = defaultdict(set)
    translators[user_c].add(locale_a.code)
    assert user_c.role(translators=translators) == f"Translator for {locale_a.code}"

    # Manager
    managers = defaultdict(set)
    managers[user_c].add(locale_a.code)
    assert user_c.role(managers=managers) == f"Manager for {locale_a.code}"


@pytest.mark.django_db
def test_user_locale_role(user_a, user_b, user_c, locale_a):
    # Default role
    assert user_a.locale_role(locale_a) == "Contributor"

    # Superuser
    user_a.is_superuser = True
    assert user_a.locale_role(locale_a) == "Admin"

    # Fake user object
    imported = User(username="Imported")
    assert imported.locale_role(locale_a) == "System User"

    # System user
    user_b.profile.system_user = True
    assert user_b.locale_role(locale_a) == "System User"

    # Translator
    locale_a.translators_group.user_set.add(user_c)
    assert user_c.locale_role(locale_a) == "Translator"

    # Manager
    locale_a.managers_group.user_set.add(user_c)
    assert user_c.locale_role(locale_a) == "Manager"

    # Admin and Manager
    locale_a.managers_group.user_set.add(user_a)
    assert user_a.locale_role(locale_a) == "Manager"


@pytest.mark.django_db
def test_user_status(user_a, user_b, user_c, user_d, locale_a, project_a):
    # New User
    assert user_a.status(locale_a, project_a)[1] == "New User"

    # Fake user object
    imported = User(username="Imported")
    assert imported.status(locale_a, project_a)[1] == ""

    # Admin
    user_a.is_superuser = True
    assert user_a.status(locale_a, project_a)[1] == "Admin"

    # Manager
    locale_a.managers_group.user_set.add(user_b)
    assert user_b.status(locale_a, project_a)[1] == "Team Manager"

    # Translator
    locale_a.translators_group.user_set.add(user_c)
    assert user_c.status(locale_a, project_a)[1] == "Translator"

    # PM
    project_a.contact = user_d
    assert user_d.status(locale_a, project_a)[1] == "Project Manager"
