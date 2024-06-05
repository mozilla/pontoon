import pytest

from django.core.management import call_command

from pontoon.base.models import User


@pytest.mark.django_db
def test_cmd_createsuperuser():
    """
    Check if that's possible to create user.
    Test against possible regressions in User model.
    """
    username = "superuser@example.com"
    call_command(
        "createsuperuser", email=username, username=username, interactive=False
    )
    user = User.objects.get(username=username)
    assert user.email == username
    assert user.is_superuser
