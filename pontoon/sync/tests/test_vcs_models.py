from __future__ import absolute_import

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
from pontoon.sync.vcs.models import (
    VCSConfiguration,
    VCSResource,
    VCSProject,
)


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
            self.vcs_project.resource_paths_without_config = Mock(return_value=[
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
            self.vcs_project.resource_paths_without_config = Mock(return_value=[
                '/root/foo.pot',
                '/root/meh/bar.pot'
            ])

            assert_equal(
                list(self.vcs_project.relative_resource_paths()),
                ['foo.po', 'meh/bar.po']
            )

    def test_source_directory_pc(self):
        """
        If project configuration provided, use source repository checkout path
        as source directory path.
        """
        self.vcs_project.configuration = Mock(return_value=[True])

        assert_equal(
            self.vcs_project.source_directory_path,
            self.vcs_project.db_project.source_repository.checkout_path
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

    @patch.object(Repository, 'checkout_path', new_callable=PropertyMock)
    def test_resource_paths_with_config(self, checkout_path_mock):
        """
        If project configuration provided, use it to collect absolute paths to all
        source resources within the source repository checkout path.
        """
        checkout_path_mock.return_value = PROJECT_CONFIG_CHECKOUT_PATH
        self.vcs_project.db_project.configuration_file = 'l10n.toml'
        self.vcs_project.configuration = VCSConfiguration(self.vcs_project)

        assert_equal(
            sorted(list(
                self.vcs_project.resource_paths_with_config()
            )),
            sorted([
                os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'values/strings.properties'),
                os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'values/strings_child.properties'),
                os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'values/strings_reality.properties'),
            ])
        )

    @patch.object(VCSProject, 'source_directory_path', new_callable=PropertyMock)
    def test_resource_paths_without_config_region_properties(self, source_directory_path_mock):
        """
        If a project has a repository_url in pontoon.base.MOZILLA_REPOS,
        resource_paths_without_config should ignore files named
        "region.properties".
        """
        source_directory_path_mock.return_value = '/root'
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
                list(self.vcs_project.resource_paths_without_config()),
                [os.path.join('/root', 'foo.pot')]
            )

    @patch.object(VCSProject, 'source_directory_path', new_callable=PropertyMock)
    def test_resource_paths_without_config_exclude_hidden(self, source_directory_path_mock):
        """
        We should filter out resources that are contained in the hidden paths.
        """
        source_directory_path_mock.return_value = '/root'
        hidden_paths = (
            ('/root/.hidden_folder/templates', [], ('bar.pot',)),
            ('/root/templates', [], ('foo.pot',)),
        )
        with patch(
            'pontoon.sync.vcs.models.scandir.walk', wraps=scandir, return_value=hidden_paths
        ):
            assert_equal(
                list(self.vcs_project.resource_paths_without_config()),
                ['/root/templates/foo.pot']
            )


class VCSConfigurationTests(TestCase):
    toml = 'l10n.toml'

    def setUp(self):
        self.locale, _ = Locale.objects.get_or_create(code='fr')

        self.repository = RepositoryFactory()
        self.db_project = ProjectFactory.create(
            repositories=[self.repository],
        )

        checkout_path_patch = patch.object(
            Repository,
            'checkout_path',
            new_callable=PropertyMock,
            return_value=PROJECT_CONFIG_CHECKOUT_PATH
        )
        self.mock_checkout_path = checkout_path_patch.start()
        self.addCleanup(checkout_path_patch.stop)

        self.resource_strings = ResourceFactory.create(
            project=self.db_project,
            path='values/strings.properties',
        )
        self.resource_strings_reality = ResourceFactory.create(
            project=self.db_project,
            path='values/strings_reality.properties',
        )
        self.resource_strings_child = ResourceFactory.create(
            project=self.db_project,
            path='values/strings_child.properties',
        )

        # Make sure VCSConfiguration instance is initialized
        self.db_project.configuration_file = self.toml
        self.vcs_project = VCSProject(
            self.db_project,
            locales=[self.locale]
        )

        self.vcs_project.configuration.configuration_path = os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH,
            self.db_project.configuration_file,
        )

    def test_add_locale(self):
        config = self.vcs_project.configuration.parsed_configuration
        locale_code = 'new-locale-code'

        assert_false(locale_code in config.all_locales)

        self.vcs_project.configuration.add_locale(locale_code)

        assert_true(locale_code in config.locales)

    def test_get_or_set_project_files_reference(self):
        self.vcs_project.configuration.add_locale = Mock()
        locale_code = None

        assert_equal(
            self.vcs_project.configuration.get_or_set_project_files(
                locale_code,
            ).locale,
            locale_code,
        )

        assert_false(self.vcs_project.configuration.add_locale.called)

    def test_get_or_set_project_files_l10n(self):
        self.vcs_project.configuration.add_locale = Mock()
        locale_code = self.locale.code

        assert_equal(
            self.vcs_project.configuration.get_or_set_project_files(
                locale_code,
            ).locale,
            locale_code,
        )

        assert_false(self.vcs_project.configuration.add_locale.called)

    def test_get_or_set_project_files_new_locale(self):
        self.vcs_project.configuration.add_locale = Mock()
        locale_code = 'new-locale-code'

        assert_equal(
            self.vcs_project.configuration.get_or_set_project_files(
                locale_code,
            ).locale,
            locale_code,
        )

        assert_true(self.vcs_project.configuration.add_locale.called)

    def test_l10n_path(self):
        reference_path = os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH,
            'values/strings.properties',
        )

        l10n_path = os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH,
            'values-fr/strings.properties',
        )

        assert_equal(
            self.vcs_project.configuration.l10n_path(
                self.locale,
                reference_path,
            ),
            l10n_path,
        )

    def test_locale_resources(self):
        assert_equal(
            sorted(
                self.vcs_project.configuration.locale_resources(self.locale),
                key=lambda r: r.path
            ),
            [
                self.resource_strings,
                self.resource_strings_child,
                self.resource_strings_reality,
            ],
        )


class GrandFatheredVCSConfigurationTest(VCSConfigurationTests):
    toml = 'grandfather.toml'


def setUpResource(self):
    self.repository = RepositoryFactory()
    self.db_project = ProjectFactory.create(
        repositories=[self.repository],
    )

    checkout_path_patch = patch.object(
        Repository,
        'checkout_path',
        new_callable=PropertyMock,
        return_value=PROJECT_CONFIG_CHECKOUT_PATH
    )
    self.mock_checkout_path = checkout_path_patch.start()
    self.addCleanup(checkout_path_patch.stop)

    # Make sure VCSConfiguration instance is initialized
    self.db_project.configuration_file = 'l10n.toml'
    self.vcs_project = VCSProject(
        self.db_project,
        locales=[self.locale]
    )

    self.vcs_project.configuration.configuration_path = os.path.join(
        PROJECT_CONFIG_CHECKOUT_PATH,
        self.db_project.configuration_file,
    )


class VCSConfigurationFullLocaleTests(TestCase):
    def setUp(self):
        self.locale, _ = Locale.objects.get_or_create(code='fr')
        setUpResource(self)

    def test_vcs_resource(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, 'values/strings.properties', [self.locale])
        assert_equal(
            r.files[self.locale].path,
            os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'values-fr/strings.properties')
        )

    def test_vcs_resource_path(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, 'values/strings_reality.properties', [self.locale])
        assert_equal(
            r.files[self.locale].path,
            os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'values-fr/strings_reality.properties')
        )

    def test_vcs_resource_child(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, 'values/strings_child.properties', [self.locale])
        assert_equal(
            r.files[self.locale].path,
            os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'values-fr/strings_child.properties')
        )


class VCSConfigurationPartialLocaleTests(TestCase):
    def setUp(self):
        self.locale, _ = Locale.objects.get_or_create(code='sl')
        setUpResource(self)

    def test_vcs_resource(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, 'values/strings.properties', [self.locale])
        assert_equal(
            r.files[self.locale].path,
            os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, 'values-sl/strings.properties')
        )

    def test_vcs_resource_path(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, 'values/strings_reality.properties', [self.locale])
        assert_equal(
            r.files,
            {}
        )

    def test_vcs_resource_child(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, 'values/strings_child.properties', [self.locale])
        assert_equal(
            r.files,
            {}
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
