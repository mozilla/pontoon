from textwrap import dedent
from unittest.mock import Mock, patch

import pytest

from pontoon.sync.repositories import get_repo


class CONTAINS:
    """
    Helper class that is considered equal to any object that contains
    elements the elements passed to it.

    Used mostly in conjunction with Mock.assert_called_with to test if
    a string argument contains certain substrings:

    >>> mock_function('foobarbaz')
    >>> mock_function.assert_called_with(CONTAINS('bar'))  # Passes
    """

    def __init__(self, *args):
        self.items = args

    def __eq__(self, other):
        return all(item in other for item in self.items)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<CONTAINS {}>".format(",".join(repr(item) for item in self.items))


@patch("pontoon.sync.repositories.git.log")
@patch("subprocess.Popen")
def test_git_revision(mock_popen, mock_log):
    attrs = {"communicate.return_value": (b"output", b"stderr"), "returncode": 1}
    mock_popen.return_value = Mock(**attrs)
    assert get_repo("git").revision("path/") is None
    mock_log.error.assert_called_with(CONTAINS("stderr", "rev-parse", "path/"))


@patch("pontoon.sync.repositories.hg.log")
@patch("subprocess.Popen")
def test_hg_revision(mock_popen, mock_log):
    attrs = {"communicate.return_value": (b"output", b"stderr"), "returncode": 1}
    mock_popen.return_value = Mock(**attrs)
    assert get_repo("hg").revision("path/") is None
    mock_log.error.assert_called_with(CONTAINS("stderr", "identify", "path/"))


# Shell output of a repository with two changed and two removed files
GIT_CHANGED_FILES = dedent(
    """
    M changed_file1.properties
    M changed_file2.properties
    D removed_file1.properties
    D removed_file2.properties
    """
).encode()

HG_CHANGED_FILES = dedent(
    """
    M changed_file1.properties
    M changed_file2.properties
    R removed_file1.properties
    R removed_file2.properties
    """
).encode()


@pytest.mark.parametrize(
    "repo_type, shell_output",
    [("git", GIT_CHANGED_FILES), ("hg", HG_CHANGED_FILES)],
)
@patch("subprocess.Popen")
def test_changed_files(mock_popen, repo_type, shell_output):
    attrs = {"communicate.return_value": (shell_output, None), "returncode": 0}
    mock_popen.return_value = Mock(**attrs)
    delta = get_repo(repo_type).changed_files("/path", "1")
    assert mock_popen.called
    assert delta == (
        ["changed_file1.properties", "changed_file2.properties"],
        ["removed_file1.properties", "removed_file2.properties"],
        [],
    )


@pytest.mark.parametrize("repo_type", ["git", "hg"])
@patch("subprocess.Popen")
def test_changed_files_error(mock_popen, repo_type):
    attrs = {"communicate.return_value": (b"", None), "returncode": 1}
    mock_popen.return_value = Mock(**attrs)
    assert get_repo(repo_type).changed_files("path", "1") is None
    assert mock_popen.called
