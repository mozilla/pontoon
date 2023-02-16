import pytest

from collections import defaultdict
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
