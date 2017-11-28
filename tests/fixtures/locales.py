
import functools

import pytest

from pontoon.base.models import Locale


@pytest.fixture
def locale0():
    """Locale 0"""
    return Locale.objects.get(code="locale0")


@pytest.fixture
def locale1():
    """Locale 1"""
    return Locale.objects.get(code="locale1")


@pytest.fixture
def localeX():
    """Locale X - empty locale"""
    return Locale.objects.get(code="localeX")


@pytest.fixture
def locale_factory(factory):
    """Locale factory
    create locales in a hurry!

    Provides an locale factory function that accepts the following args:

    :arg int `batch`: number of locales to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the locales
    """

    def instance_attrs(instance, i):
        if not instance.code:
            instance.code = "factorylocale%s" % i

    return functools.partial(
        factory, Model=Locale, instance_attrs=instance_attrs)
