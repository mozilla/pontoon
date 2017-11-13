
import pytest

from pontoon.base.models import Resource


@pytest.fixture
def resource0(project0):
    return Resource.objects.create(
        project=project0, path="resource0.po", format="po")


@pytest.fixture
def resource1(project1):
    return Resource.objects.create(
        project=project1, path="resource1.po", format="po")
