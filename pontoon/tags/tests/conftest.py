import pytest

from pontoon.test.factories import UserFactory
from .fixtures import *  # noqa


@pytest.fixture
def admin():
    """Admin - a superuser"""
    return UserFactory.create(
        username="admin",
        is_superuser=True,
    )
