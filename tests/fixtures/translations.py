
import functools

import pytest

from pontoon.base.models import Translation


@pytest.fixture
def translation0(locale0, entity0, user0):
    """Translation 0"""
    return Translation.objects.get(entity=entity0, locale=locale0)


@pytest.fixture
def translation1(locale1, entity1, user1):
    """Translation 1"""
    return Translation.objects.get(entity=entity1, locale=locale1)


@pytest.fixture
def approved0(translation0):
    """Approved translation 0"""
    translation0.approved = True
    translation0.save()
    return translation0


@pytest.fixture
def translation_factory(factory):
    """Translation factory
    create translations in a hurry!

    Provides a translation factory function that accepts the following args:

    :arg int `batch`: number of translations to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the translations
    """

    def instance_attrs(instance, i):
        if not instance.string:
            instance.string = "Translation for: %s" % i

    return functools.partial(
        factory, Model=Translation, instance_attrs=instance_attrs)
