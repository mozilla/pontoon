
import pytest

from pontoon.base.models import Project


@pytest.fixture
def project0():
    return Project.objects.create(slug="project0", name="Project 0")


@pytest.fixture
def project1():
    return Project.objects.create(slug="project1", name="Project 1")


@pytest.fixture
def projectX():
    return Project.objects.create(slug="projectX", name="Project X")
