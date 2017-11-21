
import pytest

from pontoon.base.models import Resource


@pytest.fixture
def resource0(project0):
    """Resource 0"""
    return Resource.objects.get(project=project0, path="resource0.po")


@pytest.fixture
def resource1(project1):
    """Resource 1"""
    return Resource.objects.get(project=project1, path="resource1.po")


@pytest.fixture
def resourceX(projectX):
    """Resource X - empty resource"""
    return Resource.objects.create(
        project=projectX, path="resourceX.po", format="po")
