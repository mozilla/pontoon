from django.core.management.base import CommandError

from django_nose.tools import assert_false, assert_raises
from mock import patch, PropertyMock

from pontoon.base.models import Project
from pontoon.base.tests import ProjectFactory, TestCase
from pontoon.sync.management.commands import sync_projects


class CommandTests(TestCase):
    def setUp(self):
        super(CommandTests, self).setUp()
        self.command = sync_projects.Command()
        self.command.verbosity = 0
        self.command.no_commit = False
        self.command.no_pull = False

        Project.objects.filter(slug='pontoon-intro').delete()

        self.mock_sync_project = self.patch_object(sync_projects, 'sync_project')

    def execute_command(self, *args, **kwargs):
        kwargs.setdefault('verbosity', 0)
        kwargs.setdefault('no_commit', False)
        kwargs.setdefault('no_pull', False)

        self.command.handle(*args, **kwargs)

    def test_disabled_projects(self):
        """Only sync projects that aren't disabled."""
        ProjectFactory.create(disabled=True)
        active_project = ProjectFactory.create(disabled=False)

        self.execute_command()
        self.mock_sync_project.delay.assert_called_with(
            active_project.pk,
            no_pull=False,
            no_commit=False
        )

    def test_project_slugs(self):
        """
        If project slugs are passed to Command.handle, only sync projects
        matching those slugs.
        """
        ignore_project, handle_project = ProjectFactory.create_batch(2)

        self.execute_command(handle_project.slug)
        self.mock_sync_project.delay.assert_called_with(
            handle_project.pk,
            no_pull=False,
            no_commit=False
        )

    def test_no_matching_projects(self):
        """
        If no projects are found that match the given slugs, raise a
        CommandError.
        """
        with assert_raises(CommandError):
            self.execute_command('does-not-exist')

    def test_cant_commit(self):
        """If project.can_commit is False, do not sync it."""
        project = ProjectFactory.create()

        with patch.object(Project, 'can_commit', new_callable=PropertyMock) as can_commit:
            can_commit.return_value = False

            self.execute_command(project.slug)
            assert_false(self.mock_sync_project.delay.called)

    def test_options(self):
        project = ProjectFactory.create()
        self.execute_command(no_pull=True, no_commit=True)
        self.mock_sync_project.delay.assert_called_with(
            project.pk,
            no_pull=True,
            no_commit=True
        )
