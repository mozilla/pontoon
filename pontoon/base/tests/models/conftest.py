import pytest

from pontoon.test.factories import RepositoryFactory


@pytest.fixture
def repo_git(project_a):
    """Repo (git) 0"""
    return RepositoryFactory.create(
        type="git",
        project=project_a,
        url="repo_git0",
    )


@pytest.fixture
def repo_hg(project_a):
    """Repo (hg) 0"""
    return RepositoryFactory.create(
        type="hg",
        project=project_a,
        url="repo_hg0",
    )
