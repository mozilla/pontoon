
import pytest

from pontoon.base.models import Entity


@pytest.fixture
def entity0(resource0):
    return Entity.objects.create(
        resource=resource0, string="entity0")


@pytest.fixture
def entity1(resource1):
    return Entity.objects.create(
        resource=resource1, string="entity1")
