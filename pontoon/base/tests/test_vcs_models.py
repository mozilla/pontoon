import os.path

from django_nose.tools import assert_equal
from mock import Mock, patch, PropertyMock

from pontoon.base.models import Project
from pontoon.base.tests import CONTAINS, ProjectFactory, TestCase
from pontoon.base.formats.base import ParseError
from pontoon.base.vcs_models import VCSProject


TEST_CHECKOUT_PATH = os.path.join(os.path.dirname(__file__), 'directory_detection_test')


class VCSProjectTests(TestCase):
    def setUp(self):
        # Force the checkout path to point to a test directory to make
        # resource file loading pass during tests.
        checkout_path_patch = patch.object(
            Project,
            'checkout_path',
            new_callable=PropertyMock,
            return_value=TEST_CHECKOUT_PATH
        )
        checkout_path_patch.start()
        self.addCleanup(checkout_path_patch.stop)

        self.project = ProjectFactory.create()
        self.vcs_project = VCSProject(self.project)

    def test_relative_resource_paths(self):
        self.vcs_project.source_directory_path = Mock(return_value='/root/')
        self.vcs_project.resources_for_path = Mock(return_value=[
            '/root/foo.po',
            '/root/meh/bar.po'
        ])

        assert_equal(
            list(self.vcs_project.relative_resource_paths()),
            ['foo.po', 'meh/bar.po']
        )

    def test_relative_resource_paths_pot(self):
        """
        If a resource ends in .pot, replace the extension with .po since
        relative paths are used within non-source locales that do not
        have .pot files.
        """
        self.vcs_project.source_directory_path = Mock(return_value='/root/')
        self.vcs_project.resources_for_path = Mock(return_value=[
            '/root/foo.pot',
            '/root/meh/bar.pot'
        ])

        assert_equal(
            list(self.vcs_project.relative_resource_paths()),
            ['foo.po', 'meh/bar.po']
        )

    def test_source_directory_path_no_resource(self):
        """
        When searching for source directories, do not match directories that
        do not contain resource files.
        """
        assert_equal(
            self.vcs_project.source_directory_path(),
            os.path.join(TEST_CHECKOUT_PATH, 'real_resources', 'templates')
        )

    def test_resources_parse_error(self):
        """
        If VCSResource() raises a ParseError while loading, log an error
        and skip the resource.
        """
        self.vcs_project.relative_resource_paths = Mock(return_value=['failure', 'success'])

        # Fail only if the path is failure so we can test the ignore.
        def vcs_resource_constructor(project, path):
            if path == 'failure':
                raise ParseError('error message')
            else:
                return 'successful resource'

        with patch('pontoon.base.vcs_models.VCSResource') as MockVCSResource, \
             patch('pontoon.base.vcs_models.log') as mock_log:
            MockVCSResource.side_effect = vcs_resource_constructor

            assert_equal(self.vcs_project.resources, {'success': 'successful resource'})
            mock_log.error.assert_called_with(CONTAINS('failure', 'error message'))
