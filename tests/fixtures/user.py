
from collections import OrderedDict

import pytest

from django.contrib.auth import get_user_model

from pontoon.base.models import User


def _create_users(**kwargs):
    """
    Helper method, creates contributor with given translations counts.
    """
    batch = kwargs.pop("batch", 1)
    n = (
        User.objects.values_list("pk", flat=True)
                    .order_by("-pk").first()
        or 0) + 1
    contributors = OrderedDict()
    for i in range(0, batch):
        username = "test%s" % (n + i)
        contributors[username] = User(
            username=username,
            email="test%s@example.com" % (n + i))
    User.objects.bulk_create(contributors.values())
    return contributors.values()


@pytest.fixture
def user0():
    return get_user_model().objects.create(username="user0")


@pytest.fixture
def user1():
    return get_user_model().objects.create(username="user1")


@pytest.fixture
def user_factory():
    return _create_users
