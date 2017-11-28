
import functools

import pytest

from pontoon.base.models import ProjectLocale


@pytest.fixture
def project_locale0(project0, locale0):
    """Project locale 0"""
    return ProjectLocale.objects.get(project=project0, locale=locale0)


@pytest.fixture
def project_locale1(project1, locale1):
    """Project locale 1"""
    return ProjectLocale.objects.get(project=project1, locale=locale1)


@pytest.fixture
def project_locale_factory(factory):
    """ProjectLocale factory
    create project locales in a hurry!

    Provides a project locale factory function that accepts the
    following args:

    :arg int `batch`: number of project locales to instantiate,
        defaults to len of `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the
        project locales
    """
    return functools.partial(factory, Model=ProjectLocale)
