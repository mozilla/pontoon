from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import Mock

from pontoon.base.models import Project, Repository
from pontoon.sync.checkouts import Checkout, Checkouts
from pontoon.sync.paths import get_paths
from pontoon.sync.tests.utils import FileTree, build_file_tree


def test_no_config_one_repo():
    tree: FileTree = {
        "repo": {
            "en-US": {"bar.ftl": "", "foo.pot": "", ".other.ftl": ""},
            "fr": {"bar.ftl": "", "foo.po": "", ".other.ftl": ""},
            ".ignore": {"other.ftl": ""},
        }
    }
    with TemporaryDirectory() as root:
        build_file_tree(root, tree)
        mock_project = Mock(Project, checkout_path=root, configuration_file=None)
        mock_checkout = Mock(
            Checkout, path=join(root, "repo"), removed=[join("en-US", "missing.ftl")]
        )
        paths = get_paths(mock_project, Checkouts(mock_checkout, mock_checkout))
        assert paths.ref_root == join(root, "repo", "en-US")
        assert paths.base == join(root, "repo")
        assert set(paths.ref_paths) == set(
            join(root, "repo", "en-US", file)
            for file in ["bar.ftl", "foo.pot", "missing.ftl"]
        )
        assert paths.find_reference("fr/bar.ftl") == (
            join(root, "repo", "en-US", "bar.ftl"),
            {"locale": "fr"},
        )
        assert paths.find_reference("fr/foo.po") == (
            join(root, "repo", "en-US", "foo.pot"),
            {"locale": "fr"},
        )
        assert paths.find_reference("fr/missing.ftl") == (
            join(root, "repo", "en-US", "missing.ftl"),
            {"locale": "fr"},
        )
        assert paths.find_reference("fr/.other.ftl") is None


def test_no_config_two_repos():
    tree: FileTree = {
        "source": {"bar.ftl": "", "foo.pot": "", ".other.ftl": ""},
        "target": {
            "de": {"bar.ftl": "", "foo.po": ""},
            "fr": {"bar.ftl": "", "foo.po": ""},
            ".ignore": {"other.ftl": ""},
        },
    }
    with TemporaryDirectory() as root:
        build_file_tree(root, tree)
        mock_project = Mock(Project, checkout_path=root, configuration_file=None)
        checkouts = Checkouts(
            Mock(Checkout, path=join(root, "source"), removed=[]),
            Mock(Checkout, path=join(root, "target")),
        )
        paths = get_paths(mock_project, checkouts)
        assert paths.ref_root == join(root, "source")
        assert paths.base == join(root, "target")
        assert set(paths.ref_paths) == set(
            join(root, "source", file) for file in ["bar.ftl", "foo.pot"]
        )
        assert paths.find_reference(join(root, "target", "de", "bar.ftl")) == (
            join(root, "source", "bar.ftl"),
            {"locale": "de"},
        )
        assert paths.find_reference(join(root, "target", "de", "foo.po")) == (
            join(root, "source", "foo.pot"),
            {"locale": "de"},
        )


def test_config_one_repo():
    tree: FileTree = {
        "repo": {
            "bar": {"en": {"bar.ftl": ""}, "fr": {"bar.ftl": ""}},
            "foo": {"en": {"foo.pot": ""}, "fr": {"foo.po": ""}},
            "l10n.toml": dedent(
                """\
                [[paths]]
                    reference = "bar/en/bar.ftl"
                    l10n = "bar/{locale}/bar.ftl"
                [[paths]]
                    reference = "foo/en/**"
                    l10n = "foo/{locale}/**"
                """
            ),
        }
    }
    with TemporaryDirectory() as root:
        build_file_tree(root, tree)
        mock_project = Mock(Project, checkout_path=root, configuration_file="l10n.toml")
        mock_checkout = Mock(Checkout, path=join(root, "repo"), removed=[])
        paths = get_paths(mock_project, Checkouts(mock_checkout, mock_checkout))
        assert paths.ref_root == join(root, "repo")
        assert paths.base == join(root, "repo")
        assert set(paths.ref_paths) == set(
            [
                join(root, "repo", "bar", "en", "bar.ftl"),
                join(root, "repo", "foo", "en", "foo.pot"),
            ]
        )
        assert paths.find_reference(join(root, "repo", "foo", "fr", "foo.po")) == (
            join(root, "repo", "foo", "en", "foo.pot"),
            {"locale": "fr"},
        )


def test_config_two_repos():
    tree: FileTree = {
        "source": {
            "bar": {"en": {"bar.ftl": ""}},
            "foo": {"en": {"foo.pot": ""}},
            "l10n.toml": dedent(
                """\
                [[paths]]
                    reference = "bar/en/bar.ftl"
                    l10n = "bar/{locale}/bar.ftl"
                [[paths]]
                    reference = "foo/en/**"
                    l10n = "foo/{locale}/**"
                """
            ),
        },
        "target": {
            "bar": {"fr": {"bar.ftl": ""}},
            "foo": {"fr": {"foo.po": ""}},
        },
    }
    with TemporaryDirectory() as root:
        build_file_tree(root, tree)
        mock_project = Mock(Project, checkout_path=root, configuration_file="l10n.toml")
        checkouts = Checkouts(
            Mock(Checkout, path=join(root, "source"), removed=[]),
            Mock(
                Checkout,
                path=join(root, "target"),
                repo=Mock(Repository, checkout_path=join(root, "target")),
            ),
        )
        paths = get_paths(mock_project, checkouts)
        assert paths.ref_root == join(root, "source")
        assert paths.base == join(root, "target")
        assert set(paths.ref_paths) == set(
            [
                join(root, "source", "bar", "en", "bar.ftl"),
                join(root, "source", "foo", "en", "foo.pot"),
            ]
        )
        assert paths.find_reference(join(root, "target", "foo", "fr", "foo.po")) == (
            join(root, "source", "foo", "en", "foo.pot"),
            {"locale": "fr"},
        )
