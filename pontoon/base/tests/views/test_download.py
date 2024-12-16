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


@pytest.mark.django_db
@pytest.mark.parametrize("two_repos", [True, False])
@pytest.mark.parametrize(
    "repo_url,expected_location",
    [
        (
            "https://github.com:gh-org/gh-repo.git",
            "https://raw.githubusercontent.com/gh-org/gh-repo/HEAD/de-Test/a.ftl",
        ),
        (
            "git@gitlab.com:gl-org/gl-repo.git",
            "https://gitlab.com/gl-org/gl-repo/-/raw/HEAD/de-Test/a.ftl?inline=false",
        ),
        ("http://example.com/tgt-repo", "https://example.com/tgt-repo"),
    ],
)
def test_download(two_repos, repo_url, expected_location):
    mock_vcs = MockVersionControl(changes=None)
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
    ):
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="de-Test")
        if two_repos:
            repo_src = RepositoryFactory(
                url="http://example.com/src-repo", source_repo=True
            )
            repo_tgt = RepositoryFactory(url=repo_url)
            project = ProjectFactory.create(
                name="test-dl",
                locales=[locale],
                repositories=[repo_src, repo_tgt],
                visibility=Project.Visibility.PUBLIC,
            )
            src_root = repo_src.checkout_path
            tgt_root = repo_tgt.checkout_path
            makedirs(src_root)
            build_file_tree(src_root, {"en-US": {"a.ftl": ""}})
            makedirs(tgt_root)
            build_file_tree(tgt_root, {"de-Test": {"a.ftl": ""}})
        else:
            repo = RepositoryFactory(url=repo_url)
            project = ProjectFactory.create(
                name="test-dl",
                locales=[locale],
                repositories=[repo],
                visibility=Project.Visibility.PUBLIC,
            )
            repo_root = repo.checkout_path
            makedirs(repo_root)
            build_file_tree(
                repo_root, {"en-US": {"a.ftl": ""}, "de-Test": {"a.ftl": ""}}
            )
        res = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale, resource=res)

        request = RequestFactory().get(
            "/translations/?code=de-Test&slug=test-dl&part=a.ftl"
        )
        request.user = UserFactory()
        response = download_translations(request)
        assert response.status_code == 302
        assert response.get("Location") == expected_location
