from datetime import datetime

import mock
from django_nose.tools import assert_equal

from pontoon.administration.management.commands import commit_projects
from pontoon.base.models import Project
from pontoon.base.tests import ProjectFactory, TestCase


class CommitProjectsTests(TestCase):
    def setUp(self):
        """
        Mock out the major functions so we can test the specific things
        that commit_projects handles.
        """
        self.command = commit_projects.Command()
        self.patches = {
            'update_from_repository': mock.patch.object(
                commit_projects, 'update_from_repository'
            ),
            'extract_to_database': mock.patch.object(
                commit_projects, 'extract_to_database'
            ),
            'dump_from_database': mock.patch.object(
                commit_projects, 'dump_from_database'
            ),
            'commit_to_vcs': mock.patch.object(
                commit_projects, 'commit_to_vcs'
            ),
            'datetime': mock.patch.object(
                commit_projects, 'datetime'
            )
        }

        super(CommitProjectsTests, self).setUp()

    def test_last_committed(self):
        """
        Ensure that the last_committed field on projects is updated when
        commit_projects is run.
        """
        self.mocks['dump_from_database'].return_value = 'fake/path.po'
        self.mocks['commit_to_vcs'].return_value = None
        self.mocks['datetime'].now.return_value = datetime(2015, 2, 1)

        no_date_project = ProjectFactory.create(
            slug='new-project', repository_type='git', last_committed=None)
        old_date_project = ProjectFactory.create(
            slug='old-project', repository_type='git', last_committed=datetime(2015, 1, 1))

        self.command.handle(no_date_project.pk, old_date_project.pk)

        # Re-fetch projects and check their dates.
        no_date_project = Project.objects.get(pk=no_date_project.pk)
        old_date_project = Project.objects.get(pk=old_date_project.pk)
        assert_equal(no_date_project.last_committed, datetime(2015, 2, 1))
        assert_equal(old_date_project.last_committed, datetime(2015, 2, 1))
