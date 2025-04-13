import io

import pytest

from django.core.management.base import CommandError

from pontoon.base.models import Project
from pontoon.base.tests import ProjectFactory, TestCase
from pontoon.sync.management.commands import sync_projects


class CommandTests(TestCase):
    def setUp(self):
        super().setUp()
        self.command = sync_projects.Command()
        self.command.verbosity = 0
        self.command.commit = True
        self.command.pull = True
        self.command.force = False
        self.command.stderr = io.StringIO()

        Project.objects.filter(slug="pontoon-intro").delete()

        self.mock_sync_project_task = self.patch_object(
            sync_projects, "sync_project_task"
        )

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
        active_project = ProjectFactory.create(
            disabled=False,
            sync_disabled=False,
        )

        self.execute_command()
        self.mock_sync_project_task.delay.assert_called_with(
            active_project.pk, pull=True, commit=True, force=False
        )

    def test_non_repository_projects(self):
        """Only sync projects with data_source=repository."""
        ProjectFactory.create(data_source=Project.DataSource.DATABASE)
        repo_project = ProjectFactory.create(data_source=Project.DataSource.REPOSITORY)

        self.execute_command()
        self.mock_sync_project_task.delay.assert_called_with(
            repo_project.pk, pull=True, commit=True, force=False
        )

    def test_project_slugs(self):
        """
        If project slugs are passed to Command.handle, only sync projects
        matching those slugs.
        """
        ignore_project, handle_project = ProjectFactory.create_batch(2)

        self.execute_command(projects=handle_project.slug)
        self.mock_sync_project_task.delay.assert_called_with(
            handle_project.pk, pull=True, commit=True, force=False
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

        self.mock_sync_project_task.delay.assert_called_with(
            handle_project.pk, pull=True, commit=True, force=False
        )

        assert (
            self.command.stderr.getvalue()
            == "Couldn't find projects to sync with following slugs: aaa, bbb"
        )

    def test_options(self):
        project = ProjectFactory.create()
        self.execute_command(no_pull=True, no_commit=True)
        self.mock_sync_project_task.delay.assert_called_with(
            project.pk, pull=False, commit=False, force=False
        )
