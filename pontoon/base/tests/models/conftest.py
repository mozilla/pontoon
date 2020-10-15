import pytest

from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslatedResourceFactory,
)


@pytest.fixture
def repo_file(project_a):
    """Repo (file) 0"""
    return RepositoryFactory.create(type="file", project=project_a, url="repo_file0",)


@pytest.fixture
def repo_git(project_a):
    """Repo (git) 0"""
    return RepositoryFactory.create(type="git", project=project_a, url="repo_git0",)


@pytest.fixture
def repo_hg(project_a):
    """Repo (hg) 0"""
    return RepositoryFactory.create(type="hg", project=project_a, url="repo_hg0",)


@pytest.fixture
def locale_parts(project_b, locale_c, locale_b):
    ProjectLocaleFactory.create(project=project_b, locale=locale_c)
    ProjectLocaleFactory.create(project=project_b, locale=locale_b)
    resourceX = ResourceFactory.create(
        project=project_b, path="resourceX.po", format="po",
    )
    entityX = EntityFactory.create(resource=resourceX, string="entityX")
    resourceX.total_strings = 1
    resourceX.save()
    TranslatedResourceFactory.create(locale=locale_c, resource=resourceX)
    return locale_c, locale_b, entityX
