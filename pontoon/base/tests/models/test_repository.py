import os

from urllib.parse import urlparse

import pytest

from django.core.exceptions import ValidationError

from pontoon.base.models.repository import repository_url_validator


@pytest.mark.django_db
def test_repo_checkout_path(repo_git, settings):
    """checkout_path should be determined by the repo URL."""
    # im a bit unclear about the mix of os.path and urlparse here
    # how would this work on windows <> linux ?
    assert repo_git.checkout_path == os.path.join(
        *[repo_git.project.checkout_path] + urlparse(repo_git.url).path.split("/")
    )
    settings.MEDIA_ROOT = "/media/root"
    assert repo_git.checkout_path == os.path.join(
        *[repo_git.project.checkout_path] + urlparse(repo_git.url).path.split("/")
    )
    assert repo_git.project.checkout_path.startswith("/media/root")


@pytest.mark.django_db
def test_repo_checkout_path_source_repo(settings, repo_git):
    """
    The checkout_path for a source repo should not end with a templates
    directory.
    """
    repo_git.source_repo = True
    repo_git.url = "https://example.com/path/to/locale/"
    repo_git.save()
    assert repo_git.checkout_path == (
        f"{settings.MEDIA_ROOT}/projects/{repo_git.project.slug}/path/to/locale"
    )


@pytest.mark.django_db
def test_repo_checkout_path_scp_url(settings, repo_git):
    """
    Exclude username and host from local paths for SCP-like git URLs.
    """
    repo_git.url = "git@github.com:mozilla-l10n/repo-l10n.git"
    repo_git.save()
    assert repo_git.checkout_path == (
        f"{settings.MEDIA_ROOT}/projects/{repo_git.project.slug}/mozilla-l10n/repo-l10n.git"
    )


def test_repository_url_validator():
    """
    The validity of the Repository URL.
    """
    regular_url = "https://example.com/"
    assert repository_url_validator(regular_url) is None

    git_scp_url = "git@github.com:user/repository.git"
    assert repository_url_validator(git_scp_url) is None

    invalid_url = "--evil=parameter"
    with pytest.raises(ValidationError):
        repository_url_validator(invalid_url)
