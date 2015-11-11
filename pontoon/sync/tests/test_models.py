from django_nose.tools import assert_equal, assert_false, assert_is_none, assert_true

from pontoon.base.tests import ProjectFactory, RepositoryFactory, TestCase
from pontoon.base.utils import aware_datetime
from pontoon.sync.tests import (
    ProjectSyncLogFactory,
    RepositorySyncLogFactory,
    SyncLogFactory,
)


class SyncLogTests(TestCase):
    def test_end_time_unfinished(self):
        """If a job is unfinished, it's end_time is None."""
        sync_log = SyncLogFactory.create()

        # Create repo without existing log so sync is unfinished.
        repo = RepositoryFactory.create()
        ProjectSyncLogFactory.create(sync_log=sync_log, project__repositories=[repo])

        assert_is_none(sync_log.end_time)

    def test_end_time(self):
        """
        Return the latest end time among repo sync logs for this log.
        """
        sync_log = SyncLogFactory.create()
        RepositorySyncLogFactory.create(project_sync_log__sync_log=sync_log,
                                        end_time=aware_datetime(2015, 1, 1))
        RepositorySyncLogFactory.create(project_sync_log__sync_log=sync_log,
                                        end_time=aware_datetime(2015, 1, 2))

        assert_equal(sync_log.end_time, aware_datetime(2015, 1, 2))

    def test_finished(self):
        sync_log = SyncLogFactory.create()

        # Create repo without existing log so sync is unfinished.
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(
            sync_log=sync_log, project__repositories=[repo])

        # Sync isn't finished until all repos are finished.
        assert_false(sync_log.finished)

        repo_log = RepositorySyncLogFactory.create(
            repository=repo,
            project_sync_log=project_sync_log,
            start_time=aware_datetime(2015, 1, 1),
            end_time=None
        )
        assert_false(sync_log.finished)

        repo_log.end_time = aware_datetime(2015, 1, 2)
        repo_log.save()
        assert_true(sync_log.finished)


class ProjectSyncLogTests(TestCase):
    def test_end_time_unfinished(self):
        """If a sync is unfinished, it's end_time is None."""
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(project__repositories=[repo])
        assert_is_none(project_sync_log.end_time)

    def test_end_time(self):
        """
        Return the latest end time among repo sync logs for this log.
        """
        project = ProjectFactory.create(repositories=[])
        repo1, repo2 = RepositoryFactory.create_batch(2, project=project)
        project_sync_log = ProjectSyncLogFactory.create(project=project)

        RepositorySyncLogFactory.create(project_sync_log=project_sync_log,
                                        repository=repo1,
                                        end_time=aware_datetime(2015, 1, 1))
        RepositorySyncLogFactory.create(project_sync_log=project_sync_log,
                                        repository=repo2,
                                        end_time=aware_datetime(2015, 1, 2))

        assert_equal(project_sync_log.end_time, aware_datetime(2015, 1, 2))

    def test_finished(self):
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(project__repositories=[repo])

        # Sync isn't finished until all repos are finished.
        assert_false(project_sync_log.finished)

        repo_log = RepositorySyncLogFactory.create(
            repository=repo,
            project_sync_log=project_sync_log,
            start_time=aware_datetime(2015, 1, 1),
            end_time=None
        )
        assert_false(project_sync_log.finished)

        repo_log.end_time = aware_datetime(2015, 1, 2)
        repo_log.save()
        assert_true(project_sync_log.finished)


class RepositorySyncLogTests(TestCase):
    def test_finished(self):
        log = RepositorySyncLogFactory.create(end_time=None)
        assert_false(log.finished)

        log.end_time = aware_datetime(2015, 1, 1)
        log.save()
        assert_true(log.finished)
