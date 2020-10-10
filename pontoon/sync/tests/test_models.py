from __future__ import absolute_import

from pontoon.base.tests import ProjectFactory, RepositoryFactory, TestCase
from pontoon.base.utils import aware_datetime
from pontoon.sync.models import ProjectSyncLog
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

        assert sync_log.end_time is None

    def test_end_time(self):
        """
        Return the latest end time among repo sync logs for this log.
        """
        sync_log = SyncLogFactory.create()
        RepositorySyncLogFactory.create(
            project_sync_log__sync_log=sync_log, end_time=aware_datetime(2015, 1, 1)
        )
        RepositorySyncLogFactory.create(
            project_sync_log__sync_log=sync_log, end_time=aware_datetime(2015, 1, 2)
        )

        assert sync_log.end_time == aware_datetime(2015, 1, 2)

    def test_end_time_skipped(self):
        """Include skipped repos in finding the latest end time."""
        sync_log = SyncLogFactory.create()
        RepositorySyncLogFactory.create(
            project_sync_log__sync_log=sync_log, end_time=aware_datetime(2015, 1, 1)
        )
        ProjectSyncLogFactory.create(
            sync_log=sync_log, skipped=True, skipped_end_time=aware_datetime(2015, 1, 2)
        )
        ProjectSyncLogFactory.create(
            sync_log=sync_log, skipped=True, skipped_end_time=aware_datetime(2015, 1, 4)
        )

        assert sync_log.end_time == aware_datetime(2015, 1, 4)

    def test_finished(self):
        sync_log = SyncLogFactory.create()

        # Create repo without existing log so sync is unfinished.
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(
            sync_log=sync_log, project__repositories=[repo]
        )

        # Sync isn't finished until all repos are finished.
        assert not sync_log.finished

        repo_log = RepositorySyncLogFactory.create(
            repository=repo,
            project_sync_log=project_sync_log,
            start_time=aware_datetime(2015, 1, 1),
            end_time=None,
        )
        del sync_log.finished
        assert not sync_log.finished

        repo_log.end_time = aware_datetime(2015, 1, 2)
        repo_log.save()

        del sync_log.finished
        assert sync_log.finished


class ProjectSyncLogTests(TestCase):
    def test_end_time_unfinished(self):
        """If a sync is unfinished, it's end_time is None."""
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(project__repositories=[repo])
        assert project_sync_log.end_time is None

    def test_end_time(self):
        """
        Return the latest end time among repo sync logs for this log.
        """
        project = ProjectFactory.create(repositories=[])
        source_repo, repo1, repo2 = RepositoryFactory.create_batch(3, project=project)
        project_sync_log = ProjectSyncLogFactory.create(project=project)

        RepositorySyncLogFactory.create(
            project_sync_log=project_sync_log,
            repository=repo1,
            end_time=aware_datetime(2015, 1, 1),
        )

        assert project_sync_log.end_time == aware_datetime(2015, 1, 1)

    def test_end_time_skipped(self):
        """
        If a sync is skipped, it's end_time is self.skipped_end_time.
        """
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(
            project__repositories=[repo],
            skipped=True,
            skipped_end_time=aware_datetime(2015, 1, 1),
        )
        assert project_sync_log.end_time == aware_datetime(2015, 1, 1)

    def test_status(self):
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(
            project__repositories=[repo], skipped=False
        )

        # Repos aren't finished, status should be in-progress.
        assert project_sync_log.status == ProjectSyncLog.IN_PROGRESS

        # Once repo is finished, status should be synced.
        RepositorySyncLogFactory.create(
            repository=repo,
            project_sync_log=project_sync_log,
            start_time=aware_datetime(2015, 1, 1),
            end_time=aware_datetime(2015, 1, 1, 1),
        )

        del project_sync_log.finished
        del project_sync_log.status
        assert project_sync_log.status == ProjectSyncLog.SYNCED

        # Skipped projects are just "skipped".
        skipped_log = ProjectSyncLogFactory.create(
            project__repositories=[repo], skipped=True,
        )

        assert skipped_log.status == ProjectSyncLog.SKIPPED

    def test_finished(self):
        repo = RepositoryFactory.create()
        project_sync_log = ProjectSyncLogFactory.create(project__repositories=[repo])

        # Sync isn't finished until all repos are finished.
        assert not project_sync_log.finished

        repo_log = RepositorySyncLogFactory.create(
            repository=repo,
            project_sync_log=project_sync_log,
            start_time=aware_datetime(2015, 1, 1),
            end_time=None,
        )

        del project_sync_log.finished
        assert not project_sync_log.finished

        repo_log.end_time = aware_datetime(2015, 1, 2)
        repo_log.save()

        del project_sync_log.finished
        assert project_sync_log.finished

    def test_finished_skipped(self):
        """A skipped log is considered finished."""
        skipped_log = ProjectSyncLogFactory.create(skipped=True)
        assert skipped_log.finished


class RepositorySyncLogTests(TestCase):
    def test_finished(self):
        log = RepositorySyncLogFactory.create(end_time=None)
        assert not log.finished

        log.end_time = aware_datetime(2015, 1, 1)
        log.save()

        del log.finished
        assert log.finished
