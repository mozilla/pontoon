import os.path

from django_nose.tools import assert_equal
from mock import Mock, patch, PropertyMock

from pontoon.base.models import Project
from pontoon.base.tests import ProjectFactory, TestCase


class ProjectTests(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()

    def test_relative_resource_paths(self):
        self.project.source_directory_path = Mock(return_value='/root/')
        self.project.resources_for_path = Mock(return_value=[
            '/root/foo.po',
            '/root/meh/bar.po'
        ])

        assert_equal(
            list(self.project.relative_resource_paths()),
            ['foo.po', 'meh/bar.po']
        )

    def test_relative_resource_paths_pot(self):
        """
        If a resource ends in .pot, replace the extension with .po since
        relative paths are used within non-source locales that do not
        have .pot files.
        """
        self.project.source_directory_path = Mock(return_value='/root/')
        self.project.resources_for_path = Mock(return_value=[
            '/root/foo.pot',
            '/root/meh/bar.pot'
        ])

        assert_equal(
            list(self.project.relative_resource_paths()),
            ['foo.po', 'meh/bar.po']
        )

    def test_source_directory_path_no_resource(self):
        """
        When searching for source directories, do not match directories that
        do not contain resource files.
        """
        with patch.object(Project, 'checkout_path', new_callable=PropertyMock) as checkout_path:
            test_path = os.path.join(os.path.dirname(__file__), 'directory_detection_test')
            checkout_path.return_value = test_path

            assert_equal(
                self.project.source_directory_path(),
                os.path.join(test_path, 'real_resources', 'templates')
            )
