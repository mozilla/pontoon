from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import Mock, patch

from django.test import TestCase

from pontoon.base.models import Project, Repository
from pontoon.sync.core.checkout import Checkout, checkout_repos
from pontoon.sync.tests.utils import FileTree, build_file_tree


class MockVersionControl:
    def __init__(self, changes: tuple[list[str], list[str]] | None):
        self._calls: list[tuple[str, Any]] = []
        self._changes = changes

    def commit(self, *args):
        self._calls.append(("commit", args))

    def update(self, *args):
        self._calls.append(("update", args))

    def revision(self, *args):
        self._calls.append(("revision", args))
        return "abc123"

    def changed_files(self, *args):
        self._calls.append(("changed_files", args))
        return self._changes


class CheckoutsTests(TestCase):
    def test_no_changes_with_prev_commit(self):
        mock_vcs = MockVersionControl(changes=([], []))
        mock_repo = Mock(
            Repository,
            branch="BRANCH",
            checkout_path="/foo/bar",
            last_synced_revisions={"single_locale": "def456"},
            source_repo=True,
            url="URL",
            type=Repository.Type.GIT,
        )
        with patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs):
            co = Checkout("SLUG", mock_repo, True, False)
            assert co.repo == mock_repo
            assert co.is_source
            assert co.url == "URL"
            assert co.path == "/foo/bar"
            assert co.prev_commit == "def456"
            assert co.commit == "abc123"
            assert not co.changed
            assert not co.removed
            assert mock_vcs._calls == [
                ("update", ("URL", "/foo/bar", "BRANCH")),
                ("revision", ("/foo/bar",)),
                ("changed_files", ("/foo/bar", "def456")),
            ]

            mock_vcs._calls.clear()
            co = Checkout("SLUG", mock_repo, False, False)
            assert mock_vcs._calls == [
                ("revision", ("/foo/bar",)),
                ("changed_files", ("/foo/bar", "def456")),
            ]

    def test_no_changes_with_no_prev_commit(self):
        tree: FileTree = {
            "en-US": {"bar.ftl": "", "foo.ftl": "", ".other.ftl": ""},
            "fr": {"bar.ftl": "", "foo.ftl": ""},
            ".ignore": {"other.ftl": ""},
        }
        with TemporaryDirectory() as root:
            build_file_tree(root, tree)
            mock_vcs = MockVersionControl(changes=([], []))
            mock_repo = Mock(
                Repository,
                branch="BRANCH",
                checkout_path=root,
                last_synced_revisions=None,
                source_repo=True,
                url="URL",
                type=Repository.Type.GIT,
            )
            with patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs):
                co = Checkout("SLUG", mock_repo, True, False)
                assert co.path == root
                assert co.prev_commit is None
                assert not co.removed
                assert sorted(co.changed) == [
                    "en-US/bar.ftl",
                    "en-US/foo.ftl",
                    "fr/bar.ftl",
                    "fr/foo.ftl",
                ]
                assert mock_vcs._calls == [
                    ("update", ("URL", root, "BRANCH")),
                    ("revision", (root,)),
                ]

    @patch("pontoon.sync.core.checkout.Checkout")
    def test_get_checkouts(self, _):
        with self.assertRaises(Exception) as cm:
            two_sources = Mock(**{"all.return_value": []})
            checkout_repos(Mock(Project, repositories=two_sources))
        assert str(cm.exception) == "No repository found"

        with self.assertRaises(Exception) as cm:
            two_sources = Mock(
                **{
                    "all.return_value": [
                        Mock(Repository, source_repo=True),
                        Mock(Repository, source_repo=True),
                    ]
                }
            )
            checkout_repos(Mock(Project, repositories=two_sources))
        assert str(cm.exception) == "Multiple source repositories"

        with self.assertRaises(Exception) as cm:
            two_targets = Mock(
                **{
                    "all.return_value": [
                        Mock(Repository, source_repo=False),
                        Mock(Repository, source_repo=False),
                    ]
                }
            )
            checkout_repos(Mock(Project, repositories=two_targets))
        assert str(cm.exception) == "Multiple target repositories"

        one_source = Mock(**{"all.return_value": [Mock(Repository, source_repo=True)]})
        result = checkout_repos(Mock(Project, repositories=one_source))
        assert result.source is not None
        assert result.source == result.target

        one_target = Mock(**{"all.return_value": [Mock(Repository, source_repo=False)]})
        result = checkout_repos(Mock(Project, repositories=one_target))
        assert result.source is not None
        assert result.source == result.target
