import pytest

from pontoon.base import system_users
from pontoon.base.models.user import User
from pontoon.base.system_users import get_pretranslation_authors, get_sync_user


@pytest.mark.django_db
def test_system_users_exist_and_are_flagged():
    """Every account in ALL must exist and be marked as a system user."""
    for username in system_users.ALL:
        user = User.objects.get(username=username)
        assert user.profile.system_user, f"{username} is not marked as a system user"


@pytest.mark.django_db
def test_pretranslation_authors_are_system_users():
    """Pretranslation authors must be a subset of the known system users."""
    assert set(system_users.PRETRANSLATION_AUTHORS.values()) <= set(system_users.ALL)


@pytest.mark.django_db
def test_lookups_return_the_expected_users(sync_user, gt_user, tm_user):
    """The lookups must return the accounts the constants point at."""
    assert get_sync_user() == sync_user
    assert get_pretranslation_authors() == {"gt": gt_user, "tm": tm_user}
