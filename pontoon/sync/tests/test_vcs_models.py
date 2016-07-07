import os
import os.path
from mock import call

from django_nose.tools import (
    assert_equal,
    assert_false,
    assert_true,
    assert_raises,
)
from mock import Mock, patch, PropertyMock

from pontoon.base.models import Project, ProjectLocale, TranslatedResource
from pontoon.base.tests import (
    CONTAINS,
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    TestCase,
)
from pontoon.sync.exceptions import ParseError
from pontoon.sync.tests import VCSEntityFactory, VCSTranslationFactory
from pontoon.sync.vcs.models import VCSProject, MissingSourceRepository


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

        repository_checkout_path_patch = patch(
                'pontoon.base.models.Repository.checkout_path',
                new_callable=PropertyMock,
                return_value=os.path.join(TEST_CHECKOUT_PATH, 'no_resources_test'))
        self.mock_repository_checkout_path = repository_checkout_path_patch.start()
        self.addCleanup(repository_checkout_path_patch.stop)

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
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, 'no_resources_test')
        self.mock_checkout_path.return_value = checkout_path

        assert_equal(
            self.vcs_project.source_directory_path(),
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
            self.vcs_project.source_directory_path(),
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
            self.vcs_project.source_directory_path(),
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
            self.vcs_project.source_directory_path(),
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

        with patch('pontoon.sync.vcs.models.VCSResource') as MockVCSResource, \
             patch('pontoon.sync.vcs.models.log') as mock_log:
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

        with patch('pontoon.sync.vcs.models.os', wraps=os) as mock_os, \
             patch('pontoon.sync.vcs.models.MOZILLA_REPOS', [url]):
            mock_os.walk.return_value = [
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
        with patch('pontoon.sync.vcs.models.os.walk', wraps=os, return_value=hidden_paths):
            assert_equal(
                list(self.vcs_project.resources_for_path('/root')),
                ['/root/templates/foo.pot']
            )

    def test_changed_files(self):
        """
        If full_scan is set to True, VCSProject should return all available resources in checkout_path of VCSProject.
        """

        with patch.object(VCSProject, 'full_scan', create=True, return_value=True, new_callable=PropertyMock) as mock_full_scan,\
             patch.object(VCSProject, 'changed_locales_files', return_value=[], new_callable=PropertyMock) as mock_changed_locales_files,\
             patch.object(VCSProject, 'changed_source_files', return_value=[[],[]], new_callable=PropertyMock) as mock_changed_source_files,\
             patch.object(VCSProject, 'locales', create=True, return_value=[], new_callable=PropertyMock) as mock_locales:

            # Test if full scan returns changed_files as None
            assert_equal(self.vcs_project.changed_files, None)
            assert_true(mock_full_scan.called)

            # We're testing if proper source changed files are returned
            mock_full_scan.return_value = False
            del self.vcs_project.changed_files

            assert_equal(self.vcs_project.changed_files, [])
            assert_false(mock_changed_locales_files.called)
            assert_true(mock_changed_source_files.called)

            # We're locale files should be returned if any locales are given
            locales = [object()]
            mock_locales.return_value = locales
            del self.vcs_project.changed_files

            assert_equal(self.vcs_project.changed_files, [])
            assert_true(mock_changed_locales_files.called)

    def test_changed_source_files_single_locale_repository(self):
        repository,  = self.project.repositories.all()

        with patch('pontoon.sync.vcs.models.get_changed_files') as mock_get_changed_files:
            # When there's no changed files
            mock_get_changed_files.return_value = [], []
            assert_equal(self.vcs_project.changed_source_files, ({}, {}))
            del self.vcs_project.changed_source_files

            # Check if changed files are detected properly
            mock_get_changed_files.return_value = (
                ['changed_file.po'],
                ['removed_file.po']
            )
            assert_equal(self.vcs_project.changed_source_files, (
                {'changed_file.po': []},
                {'removed_file.po': []}
            ))
            del self.vcs_project.changed_source_files

            mock_get_changed_files.return_value = (
                {'real_resources/templates/changed_file.po': []},
                {'real_resources/templates/removed_file.po': []},
            )
            # Check if paths are correctly mapped for the source
            repository.last_synced_revisions = {'single_locale': 'test_revision'}
            repository.save()
            del self.project.source_repository

            assert_equal(self.vcs_project.changed_source_files, (
                {'changed_file.po': []},
                {'removed_file.po': []}
            ))

    def test_changed_source_missing_directory(self):
        """Raise an error if project don't have any repositories."""
        self.project.repositories.all().delete()

        with assert_raises(MissingSourceRepository):
            self.vcs_project.changed_source_files()

    def test_changed_locale_files_source_repos(self):
        """
        We can't return changed locale files if repository is marked
        as a source_repo.
        """
        self.project.repositories.update(source_repo=True)

        assert_equal(self.vcs_project.changed_locales_files, {})

    def test_changed_locale_files_single_locale(self):
        repository, = self.project.repositories.all()
        repository.source_repo = False
        repository.last_synced_revisions = {'single_locale': 'aaa'}
        repository.save()

        locale1, locale2 = LocaleFactory.create_batch(2)
        ProjectLocale.objects.create(project=self.project, locale=locale1)
        ProjectLocale.objects.create(project=self.project, locale=locale2)

        with patch('pontoon.sync.vcs.models.get_changed_files') as mock_get_changed_files,\
                patch('pontoon.sync.vcs.models.locale_directory_path') as mock_locale_directory_path:
            mock_locale_directory_path.side_effect = lambda path, locale: ({
                locale1.code: os.path.join(repository.checkout_path, 'locales', locale1.code),
                locale2.code: os.path.join(repository.checkout_path, 'locales', locale2.code),
            })[locale]

            mock_get_changed_files.return_value = (
                # Changed files
                {
                    os.path.join('locales', locale1.code, 'changed1.po'),
                    os.path.join('locales', locale2.code, 'changed2.po'),
                    os.path.join('locales', locale2.code, 'changed1.po'),
                    'some_random_file',
                },
                # Removed files should be ignored
                {}
            )

            assert_equal(self.vcs_project.changed_locales_files, {
                'changed1.po': [locale2, locale1],
                'changed2.po': [locale2,]
            })
            mock_get_changed_files.assert_called_once_with(repository.type, repository.checkout_path, 'aaa')


    def test_changed_locale_files_for_multi_locale_repository(self):
        locale1, locale2 = LocaleFactory.create_batch(2)
        repository, = self.project.repositories.all()
        repository.source_repo = False
        repository.url = os.sep.join([os.path.split(repository.url)[0], '{locale_code}'])
        repository.last_synced_revisions = {locale1.code: 'aaa', locale2.code: 'bbb'}
        repository.save()

        ProjectLocale.objects.create(project=self.project, locale=locale1)
        ProjectLocale.objects.create(project=self.project, locale=locale2)

        with patch('pontoon.sync.vcs.models.get_changed_files') as mock_get_changed_files,\
                patch('pontoon.sync.vcs.models.locale_directory_path') as mock_locale_directory_path:
            mock_locale_directory_path.side_effect = lambda path, locale: ({
                locale1.code: os.path.join(repository.checkout_path, 'locales', locale1.code),
                locale2.code: os.path.join(repository.checkout_path, 'locales', locale2.code),
            })[locale]

            mock_get_changed_files.side_effect = lambda type_, checkout_path, last_revision: ({
                locale1.code: (
                    # Changed files
                    {'changed1.po'},
                    # Removed files
                    {}
                ),
                locale2.code: (
                    # Changed files
                    {'changed1.po', 'changed2.po'},
                    # Removed files
                    {}
                )
            }[checkout_path.split(os.sep)[-1]])

            assert_equal(self.vcs_project.changed_locales_files, {
                'changed1.po': [locale1, locale2],
                'changed2.po': [locale2,]
            })
            mock_get_changed_files.assert_has_calls([
                call(repository.type, repository.locale_checkout_path(locale1), 'aaa'),
                call(repository.type, repository.locale_checkout_path(locale2), 'bbb'),
            ], any_order=True)

    def test_resources_for_changed_files(self):
        with patch.object(VCSProject, 'changed_files', return_value=None, new_callable=PropertyMock) as mock_changed_files,\
                patch.object(VCSProject, 'obsolete_entities_paths', create=True, return_value=set(), new_callable=PropertyMock) as mock_obsolete_entities_paths,\
                patch.object(VCSProject, 'relative_resource_paths') as mock_relative_resource_paths,\
                patch('pontoon.sync.vcs.models.VCSResource'),\
                patch.object(Project, 'unsynced_locales', return_value=[], new_callable=PropertyMock):
            locale1, locale2 = LocaleFactory.create_batch(2)

            ProjectLocale.objects.create(project=self.project, locale=locale1)
            ProjectLocale.objects.create(project=self.project, locale=locale2)
            # all resouces should be returned because changed_files is None

            mock_relative_resource_paths.return_value = {
                'changed1.po',
                'changed2.po',
                'changed3.po'
            }

            assert_equal(set(self.vcs_project.resources.keys()), {'changed1.po', 'changed2.po', 'changed3.po'})
            del self.vcs_project.resources

            # Test if obsolete files are filtered out correctly
            mock_changed_files.return_value = {
                    'changes2.po': [],
                    'changes3.po': [],
            }
            mock_obsolete_entities_paths.return_value = set()
            import ipdb; ipdb.set_trace()
            assert_equal(set(self.vcs_project.resources.keys()), {'changes2.po', 'changed3.po'})
            del self.vcs_project.resources

            # only resources that have been marked as a changed files
            mock_changed_files.return_value = {'changed2.po': {locale1}}

            assert_equal(set(self.vcs_project.resources.keys()), {'changed2.po'})
            assert_equal(self.vcs_project.resources['changed2.po'].locales, [locale1])
        assert False


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
