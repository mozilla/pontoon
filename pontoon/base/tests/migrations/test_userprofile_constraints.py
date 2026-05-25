import pytest

from django.db import IntegrityError

from pontoon.test import factories


@pytest.mark.django_db
def test_userprofile_username_ci_unique_constraint():
    user_a = factories.UserFactory()
    user_b = factories.UserFactory()

    user_a.profile.username = "alice"
    user_a.profile.save()

    user_b.profile.username = "Alice"

    with pytest.raises(IntegrityError):
        user_b.profile.save()
