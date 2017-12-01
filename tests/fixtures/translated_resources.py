
import functools

import pytest

from pontoon.base.models import TranslatedResource


@pytest.fixture
def translated_resource0(locale0, resource0):
    """Translated Resource 0"""
    return TranslatedResource.objects.get(resource=resource0, locale=locale0)


@pytest.fixture
def translated_resource1(locale1, resource1):
    """Translated Resource 1"""
    return TranslatedResource.objects.get(resource=resource1, locale=locale1)


@pytest.fixture
def translated_resourceX(localeX, resourceX):
    """Translated Resource X"""
    return TranslatedResource.objects.create(
        resource=resourceX,
        locale=localeX)


@pytest.fixture
def translated_resource_factory(factory):
    """TranslatedResource factory
    create translated resources in a hurry!

    Provides a translated resource factory function that accepts the
    following args:

    :arg int `batch`: number of translated resources to instantiate,
        defaults to len of `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the
        translated resources
    """

    return functools.partial(factory, Model=TranslatedResource)
