from __future__ import absolute_import

from django.core.management.base import CommandError

import pytest
from mock import ANY, patch, PropertyMock
from six import StringIO

from pontoon.base.models import Project
from pontoon.base.tests import ProjectFactory, TestCase
from pontoon.base.utils import aware_datetime
from pontoon.sync.management.commands import sync_projects
from pontoon.sync.models import SyncLog


class CommandTests(TestCase):
    def setUp(self):
        super(CommandTests, self).setUp()
        self.command = sync_projects.Command()
        self.command.verbosity = 0
        self.command.no_commit = False
        self.command.no_pull = False
        self.command.force = False
        self.command.stderr = StringIO()

        Project.objects.filter(slug="pontoon-intro").delete()

        self.mock_sync_project = self.patch_object(sync_projects, "sync_project")

    def execute_command(self, *args, **kwargs):
        kwargs.setdefault("verbosity", 0)
        kwargs.setdefault("no_commit", False)
        kwargs.setdefault("no_pull", False)
        kwargs.setdefault("force", False)

        self.command.handle(*args, **kwargs)

    def test_syncable_projects_only(self):
        """
        Only sync projects that aren't disabled
        and for which sync isn't disabled.
        """
        ProjectFactory.create(disabled=True)
        ProjectFactory.create(sync_disabled=True)
        active_project = ProjectFactory.create(disabled=False, sync_disabled=False,)

        self.execute_command()
        self.mock_sync_project.delay.assert_called_with(
            active_project.pk, ANY, no_pull=False, no_commit=False, force=False,
        )

    def test_non_repository_projects(self):
        """Only sync projects with data_source=repository."""
        ProjectFactory.create(data_source="database")
        repo_project = ProjectFactory.create(data_source="repository")

        self.execute_command()
        self.mock_sync_project.delay.assert_called_with(
            repo_project.pk, ANY, no_pull=False, no_commit=False, force=False,
        )

    def test_project_slugs(self):
        """
        If project slugs are passed to Command.handle, only sync projects
        matching those slugs.
        """
        ignore_project, handle_project = ProjectFactory.create_batch(2)

        self.execute_command(projects=handle_project.slug)
        self.mock_sync_project.delay.assert_called_with(
            handle_project.pk, ANY, no_pull=False, no_commit=False, force=False,
        )

    def test_no_matching_projects(self):
        """
        If no projects are found that match the given slugs, raise a
        CommandError.
        """
        with pytest.raises(CommandError):
            self.execute_command(projects="does-not-exist")

    def test_invalid_slugs(self):
        """
        If some of projects have invalid slug, we should warn user about them.
        """
        handle_project = ProjectFactory.create()

        self.execute_command(projects=handle_project.slug + ",aaa,bbb")

        self.mock_sync_project.delay.assert_called_with(
            handle_project.pk, ANY, no_pull=False, no_commit=False, force=False,
        )

        assert (
            self.command.stderr.getvalue()
            == "Couldn't find projects with following slugs: aaa, bbb"
        )

    def test_cant_commit(self):
        """If project.can_commit is False, do not sync it."""
        project = ProjectFactory.create()

        with patch.object(
            Project, "can_commit", new_callable=PropertyMock
        ) as can_commit:
            can_commit.return_value = False

            self.execute_command(projects=project.slug)
            assert not self.mock_sync_project.delay.called

    def test_options(self):
        project = ProjectFactory.create()
        self.execute_command(no_pull=True, no_commit=True)
        self.mock_sync_project.delay.assert_called_with(
            project.pk, ANY, no_pull=True, no_commit=True, force=False
        )

    def test_sync_log(self):
        """Create a new sync log when command is run."""
        assert not SyncLog.objects.exists()

        ProjectFactory.create()
        with patch.object(sync_projects, "timezone") as mock_timezone:
            mock_timezone.now.return_value = aware_datetime(2015, 1, 1)
            self.execute_command()

        sync_log = SyncLog.objects.all()[0]
        assert sync_log.start_time == aware_datetime(2015, 1, 1)
