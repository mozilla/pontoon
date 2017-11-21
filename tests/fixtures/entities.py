# -*- coding: utf-8 -*-

import functools

import pytest

from pontoon.base.models import Entity


@pytest.fixture
def entity0(resource0):
    """Entity 0"""
    return Entity.objects.get(resource=resource0, string="entity0")


@pytest.fixture
def entity1(resource1):
    """Entity 1"""
    return Entity.objects.get(resource=resource1, string="entity1")


@pytest.fixture
def entity_factory(factory):
    """Entity factory
    create entities in a hurry!

    Provides an entity factory function that accepts the following args:

    :arg int `batch`: number of entities to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the entities
    """

    def instance_attrs(instance, i):
        if not instance.string:
            instance.string = "Entity %s" % i

    return functools.partial(
        factory, Model=Entity, instance_attrs=instance_attrs)
