
import functools

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


@pytest.fixture
def resource_factory(factory):
    """Resource factory
    create resources in a hurry!

    Provides an resource factory function that accepts the following args:

    :arg int `batch`: number of resources to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the resources
    """

    def instance_attrs(instance, i):
        if not instance.path:
            instance.path = "resource%s.po" % i

    return functools.partial(
        factory, Model=Resource, instance_attrs=instance_attrs)
