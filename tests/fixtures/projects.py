
import pytest

from pontoon.base.models import Project


@pytest.fixture
def project0():
    """Project 0"""
    return Project.objects.get(slug="project0")


@pytest.fixture
def project1():
    """Project 1"""
    return Project.objects.get(slug="project1")


@pytest.fixture
def projectX():
    """Project X - empty project"""
    return Project.objects.get(slug="projectX")
