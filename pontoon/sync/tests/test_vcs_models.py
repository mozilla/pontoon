import os
import scandir

from django_nose.tools import (
    assert_equal,
    assert_false,
    assert_true,
)
from mock import Mock, patch, PropertyMock

from pontoon.base.models import (
    Locale,
    Project,
    Repository,
)
from pontoon.base.tests import (
    CONTAINS,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TestCase,
)
from pontoon.sync.exceptions import ParseError
from pontoon.sync.tests import (
    PROJECT_CONFIG_CHECKOUT_PATH,
    VCSEntityFactory,
    VCSTranslationFactory,
)
from pontoon.sync.vcs.models import VCSProject


TEST_CHECKOUT_PATH = os.path.join(os.path.dirname(__file__), 'directory_detection_tests')


class VCSProjectTests(TestCase):
    def setUp(self):
        # Force the checkout path to point to a test directory to make
        # resource file loading pass during tests.
        checkout_path_patch = patch.object(
            Project,
            'checkout_path',
            new_callable=PropertyMock,
            return_value=os.path.join(TEST_CHECKOUT_PATH, 'no_resources_test')
        )
        self.mock_checkout_path = checkout_path_patch.start()
        self.addCleanup(checkout_path_patch.stop)

        self.project = ProjectFactory.create()
        self.vcs_project = VCSProject(self.project)

    def test_relative_resource_paths(self):
        with patch.object(
            VCSProject, 'source_directory_path', new_callable=PropertyMock, return_value='/root/'
        ):
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
        with patch.object(
            VCSProject, 'source_directory_path', new_callable=PropertyMock, return_value='/root/'
        ):
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
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, 'no_resources_test')
        self.mock_checkout_path.return_value = checkout_path

        assert_equal(
            self.vcs_project.source_directory_path,
            os.path.join(checkout_path, 'real_resources', 'templates')
        )

    def test_source_directory_scoring_templates(self):
        """
        When searching for source directories, prefer directories named
        `templates` over all others.
        """
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, 'scoring_templates_test')
        self.mock_checkout_path.return_value = checkout_path

        assert_equal(
            self.vcs_project.source_directory_path,
            os.path.join(checkout_path, 'templates')
        )

    def test_source_directory_scoring_en_US(self):
        """
        When searching for source directories, prefer directories named
        `en-US` over others besides `templates`.
        """
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, 'scoring_en_US_test')
        self.mock_checkout_path.return_value = checkout_path

        assert_equal(
            self.vcs_project.source_directory_path,
            os.path.join(checkout_path, 'en-US')
        )

    def test_source_directory_scoring_source_files(self):
        """
        When searching for source directories, prefer directories with
        source-only formats over all others.
        """
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, 'scoring_source_files_test')
        self.mock_checkout_path.return_value = checkout_path

        assert_equal(
            self.vcs_project.source_directory_path,
            os.path.join(checkout_path, 'en')  # en has pot files in it
        )

    def test_resources_parse_error(self):
        """
        If VCSResource() raises a ParseError while loading, log an error
        and skip the resource.
        """
        self.vcs_project.relative_resource_paths = Mock(return_value=['failure', 'success'])

        # Fail only if the path is failure so we can test the ignore.
        def vcs_resource_constructor(project, path, locales=None):
            if path == 'failure':
                raise ParseError('error message')
            else:
                return 'successful resource'

        changed_vcs_resources = {'success': [], 'failure': []}
        with patch('pontoon.sync.vcs.models.VCSResource') as MockVCSResource, \
            patch('pontoon.sync.vcs.models.log') as mock_log, \
            patch.object(
                VCSProject, 'changed_files', new_callable=PropertyMock,
                return_value=changed_vcs_resources
        ):
            MockVCSResource.side_effect = vcs_resource_constructor

            assert_equal(self.vcs_project.resources, {'success': 'successful resource'})
            mock_log.error.assert_called_with(CONTAINS('failure', 'error message'))

    def test_resource_for_path_region_properties(self):
        """
        If a project has a repository_url in pontoon.base.MOZILLA_REPOS,
        resources_for_path should ignore files named
        "region.properties".
        """
        url = 'https://moz.example.com'
        self.project.repositories.all().delete()
        self.project.repositories.add(RepositoryFactory.create(url=url))

        with patch('pontoon.sync.vcs.models.scandir', wraps=scandir) as mock_scandir, \
            patch(
                'pontoon.sync.vcs.models.MOZILLA_REPOS', [url]
        ):
            mock_scandir.walk.return_value = [
                ('/root', [], ['foo.pot', 'region.properties'])
            ]

            assert_equal(
                list(self.vcs_project.resources_for_path('/root')),
                [os.path.join('/root', 'foo.pot')]
            )

    def test_filter_hidden_directories(self):
        """
        We should filter out resources that are contained in the hidden paths.
        """
        hidden_paths = (
            ('/root/.hidden_folder/templates', [], ('bar.pot',)),
            ('/root/templates', [], ('foo.pot',)),
        )
        with patch(
            'pontoon.sync.vcs.models.scandir.walk', wraps=scandir, return_value=hidden_paths
        ):
            assert_equal(
                list(self.vcs_project.resources_for_path('/root')),
                ['/root/templates/foo.pot']
            )


class VCSConfigurationTests(TestCase):
    def setUp(self):
        self.locale, _ = Locale.objects.get_or_create(code='fr')

        self.repository = RepositoryFactory()
        self.db_project = ProjectFactory.create(
            repositories=[self.repository],
        )

        self.resource_strings = ResourceFactory.create(
            project=self.db_project,
            path='strings.properties',
        )
        self.resource_strings_reality = ResourceFactory.create(
            project=self.db_project,
            path='strings_reality.properties',
        )

        # Make sure VCSConfiguration instance is initialized
        self.db_project.configuration_file = 'l10n.toml'
        self.vcs_project = VCSProject(self.db_project)

    def test_locale_resources(self):
        with patch.object(
            VCSProject,
            'locale_directory_paths',
            new_callable=PropertyMock,
            return_value={
                self.locale.code: os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, self.locale.code),
            },
        ):
            with patch.object(
                Repository,
                'checkout_path',
                new_callable=PropertyMock,
                return_value=PROJECT_CONFIG_CHECKOUT_PATH,
            ):
                with patch.object(
                    VCSProject,
                    'source_directory_path',
                    new_callable=PropertyMock,
                    return_value=os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'en-US'),
                ):
                    assert_equal(
                        self.vcs_project.configuration.locale_resources(self.locale),
                        [self.resource_strings, self.resource_strings_reality],
                    )


class VCSEntityTests(TestCase):
    def test_has_translation_for(self):
        """
        Return True if a translation exists for the given locale, even
        if the translation is empty/falsey.
        """
        empty_translation = VCSTranslationFactory(strings={})
        full_translation = VCSTranslationFactory(strings={None: 'TRANSLATED'})
        entity = VCSEntityFactory()
        entity.translations = {'empty': empty_translation, 'full': full_translation}

        assert_false(entity.has_translation_for('missing'))
        assert_true(entity.has_translation_for('empty'))
        assert_true(entity.has_translation_for('full'))
