from os import mkdir
from os.path import join
from tempfile import TemporaryDirectory
from typing import Any, Dict, Union
from unittest.mock import Mock, patch

from django.test import TestCase

from pontoon.base.models import Project, Repository
from pontoon.sync.checkouts import Checkout, Checkouts
from pontoon.sync.paths import get_paths


Tree = Dict[str, Union[str, "Tree"]]


def build_file_tree(root: str, tree: Tree) -> None:
    for name, value in tree.items():
        path = join(root, name)
        if isinstance(value, str):
            with open(path, "x") as file:
                if value:
                    file.write(value)
        else:
            mkdir(path)
            build_file_tree(path, value)


class PathsTests(TestCase):
    def test_no_config_one_repo(self):
        tree: Tree = {
            "repo_url": {
                "en-US": {
                    "bar.ftl": "",
                    "foo.ftl": "",
                    ".other.ftl": "",
                },
                "fr": {
                    "bar.ftl": "",
                    "foo.ftl": "",
                },
                ".ignore": {
                    "other.ftl": "",
                },
            }
        }
        with TemporaryDirectory() as root:
            build_file_tree(root, tree)
            mock_project = Mock(Project, checkout_path=root, configuration_file=None)
            mock_checkouts = Mock(
                Checkouts,
                source=Mock(Checkout, path=join(root, "repo_url")),
            )
            paths = get_paths(mock_project, mock_checkouts)
            assert paths.ref_root == join(root, "repo_url", "en-US")
            assert paths.base == join(root, "repo_url")
