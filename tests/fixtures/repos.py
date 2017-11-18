
import pytest

from pontoon.base.models import Repository


@pytest.fixture
def repo_file0(project0):
    return Repository.objects.create(
        type="file", project=project0, url="repo_file0")


@pytest.fixture
def repo_git0(project0):
    return Repository.objects.create(
        type="git", project=project0, url="repo_git0")


@pytest.fixture
def repo_hg0(project0):
    return Repository.objects.create(
        type="hg", project=project0, url="repo_hg0")
