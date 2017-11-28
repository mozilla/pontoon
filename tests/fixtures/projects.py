
import functools

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


@pytest.fixture
def project_factory(factory):
    """Project factory
    create projects in a hurry!

    Provides an project factory function that accepts the following args:

    :arg int `batch`: number of projects to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the projects
    """

    def instance_attrs(instance, i):
        if not instance.slug:
            instance.slug = "factoryproject%s" % i
        if not instance.name:
            instance.name = "Factory Project %s" % i

    return functools.partial(
        factory, Model=Project, instance_attrs=instance_attrs)
