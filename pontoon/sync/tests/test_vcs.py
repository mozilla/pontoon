from textwrap import dedent
from unittest.mock import patch

from pontoon.sync.vcs.repositories import VCSRepository
from pontoon.base.tests import CONTAINS, TestCase


class VCSRepositoryTests(TestCase):
    def test_execute_log_error(self):
        """
        If the return code from execute is non-zero and log_errors is
        True, log an error message.
        """
        repo = VCSRepository("/path")

        with patch("pontoon.sync.vcs.repositories.execute") as mock_execute, patch(
            "pontoon.sync.vcs.repositories.log"
        ) as mock_log:
            mock_execute.return_value = 1, "output", "stderr"
            assert repo.execute("command", cwd="working_dir", log_errors=True) == (
                1,
                "output",
                "stderr",
            )
            mock_log.error.assert_called_with(
                CONTAINS("stderr", "command", "working_dir")
            )


class VCSChangedFilesTests(object):
    """
    Mixin class that unifies all tests  for changed/removed files between repositories.
    Every subclass should provide two properties:a
    * shell_output - should contain an string which is returned.
    * repository_type - a type of the repository that will be used to perform the test.
    """

    shell_output = ""
    repository_type = None

    def setUp(self):
        self.vcsrepository = VCSRepository.for_type(self.repository_type, "/path")

    def execute_success(self, *args, **kwargs):
        """
        Should be called when repository commands returns contents without error.
        """
        return 0, self.shell_output, None

    def execute_failure(self, *args, **kwargs):
        """
        Returns an error for all tests cases that validate error handling.
        """
        return 1, "", None

    def test_changed_files(self):
        with patch.object(
            self.vcsrepository, "execute", side_effect=self.execute_success
        ) as mock_execute:
            changed_files = self.vcsrepository.get_changed_files("/path", "1")
            assert mock_execute.called
            assert changed_files == [
                "changed_file1.properties",
                "changed_file2.properties",
            ]

    def test_changed_files_error(self):
        with patch.object(
            self.vcsrepository, "execute", side_effect=self.execute_failure
        ) as mock_execute:
            assert self.vcsrepository.get_changed_files("path", "1") == []
            assert mock_execute.called

    def test_removed_files(self):
        with patch.object(
            self.vcsrepository, "execute", side_effect=self.execute_success
        ) as mock_execute:
            removed_files = self.vcsrepository.get_removed_files("/path", "1")
            assert mock_execute.called
            assert removed_files == [
                "removed_file1.properties",
                "removed_file2.properties",
            ]

    def test_removed_files_error(self):
        with patch.object(
            self.vcsrepository, "execute", side_effect=self.execute_failure
        ) as mock_execute:
            assert self.vcsrepository.get_removed_files("path", "1") == []
            assert mock_execute.called


class GitChangedFilesTest(VCSChangedFilesTests, TestCase):
    repository_type = "git"
    shell_output = dedent(
        """
        M changed_file1.properties
        M changed_file2.properties
        D removed_file1.properties
        D removed_file2.properties
    """
    )


class HgChangedFilesTest(VCSChangedFilesTests, TestCase):
    repository_type = "hg"
    shell_output = dedent(
        """
        M changed_file1.properties
        M changed_file2.properties
        R removed_file1.properties
        R removed_file2.properties
    """
    )


class SVNChangedFilesTest(VCSChangedFilesTests, TestCase):
    repository_type = "svn"
    shell_output = dedent(
        """
        M changed_file1.properties
        M changed_file2.properties
        D removed_file1.properties
        D removed_file2.properties
    """
    )
