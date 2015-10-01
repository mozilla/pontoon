from django_nose.tools import assert_false
from mock import patch

from pontoon.base.tests import CONTAINS, TestCase
from pontoon.sync.tasks import sync_project


class SyncProjectTests(TestCase):
    def test_missing_project(self):
        """
        If a project with the given PK doesn't exist, log it and exit.
        """
        with patch('pontoon.sync.tasks.log') as mock_log, \
             patch('pontoon.sync.tasks.perform_sync') as mock_perform_sync:
            sync_project(99999)
            mock_log.error.assert_called_with(CONTAINS('99999'))
            assert_false(mock_perform_sync.called)
