from django_nose.tools import assert_equal
from mock import patch

from pontoon.administration.vcs import VCSRepository
from pontoon.base.tests import CONTAINS, TestCase


class VCSRepositoryTests(TestCase):
    def test_execute_log_error(self):
        """
        If the return code from execute is non-zero and log_errors is
        True, log an error message.
        """
        repo = VCSRepository('/path')

        with patch('pontoon.administration.vcs.execute') as mock_execute, \
             patch('pontoon.administration.vcs.log') as mock_log:
            mock_execute.return_value = 1, 'output', 'stderr'
            assert_equal(
                repo.execute('command', cwd='working_dir', log_errors=True),
                (1, 'output', 'stderr')
            )
            mock_log.error.assert_called_with(CONTAINS('stderr', 'command', 'working_dir'))
