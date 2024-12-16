from os import makedirs
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from django.conf import settings
from django.test import RequestFactory

from pontoon.base.models.project import Project
from pontoon.base.tests import (
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    UserFactory,
)
from pontoon.base.views import download_translations
from pontoon.sync.tests.test_checkouts import MockVersionControl
from pontoon.sync.tests.utils import build_file_tree


def _setup(root: str, tgt_url: str):
    # Database setup
    settings.MEDIA_ROOT = root
    locale = LocaleFactory.create(code="de-Test")
    repo_src = RepositoryFactory(url="http://example.com/src-repo", source_repo=True)
    repo_tgt = RepositoryFactory(url=tgt_url)
    project = ProjectFactory.create(
        name="test-dl",
        locales=[locale],
        repositories=[repo_src, repo_tgt],
        visibility=Project.Visibility.PUBLIC,
    )
    res = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
    TranslatedResourceFactory.create(locale=locale, resource=res)

    # Filesystem setup
    src_root = repo_src.checkout_path
    makedirs(src_root)
    build_file_tree(src_root, {"en-US": {"a.ftl": ""}})
    tgt_root = repo_tgt.checkout_path
    makedirs(tgt_root)
    build_file_tree(tgt_root, {"de-Test": {"a.ftl": ""}})


@pytest.mark.django_db
def test_download_github():
    mock_vcs = MockVersionControl(changes=None)
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
    ):
        _setup(root, tgt_url="https://github.com:gh-org/gh-repo.git")
        request = RequestFactory().get(
            "/translations/?code=de-Test&slug=test-dl&part=a.ftl"
        )
        request.user = UserFactory()
        response = download_translations(request)
        assert response.status_code == 302
        assert (
            response.get("Location")
            == "https://raw.githubusercontent.com/gh-org/gh-repo/HEAD/de-Test/a.ftl"
        )


@pytest.mark.django_db
def test_download_gitlab():
    mock_vcs = MockVersionControl(changes=None)
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
    ):
        _setup(root, tgt_url="git@gitlab.com:gl-org/gl-repo.git")
        request = RequestFactory().get(
            "/translations/?code=de-Test&slug=test-dl&part=a.ftl"
        )
        request.user = UserFactory()
        response = download_translations(request)
        assert response.status_code == 302
        assert (
            response.get("Location")
            == "https://gitlab.com/gl-org/gl-repo/-/raw/HEAD/de-Test/a.ftl?inline=false"
        )


@pytest.mark.django_db
def test_download_other():
    mock_vcs = MockVersionControl(changes=None)
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
    ):
        _setup(root, tgt_url="http://example.com/tgt-repo")

        request = RequestFactory().get(
            "/translations/?code=de-Test&slug=test-dl&part=a.ftl"
        )
        request.user = UserFactory()
        response = download_translations(request)
        assert response.status_code == 302
        assert response.get("Location") == "https://example.com/tgt-repo"
