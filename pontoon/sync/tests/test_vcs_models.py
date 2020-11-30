import tempfile
import os

from http.client import HTTPException
from pathlib import Path
from unittest.mock import Mock, patch, PropertyMock, MagicMock

import scandir

from pontoon.base.models import (
    Locale,
    Project,
    Repository,
)
from pontoon.base.tests import (
    CONTAINS,
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TestCase,
)
from pontoon.sync.exceptions import ParseError
from pontoon.sync.tests import (
    PROJECT_CONFIG_CHECKOUT_PATH,
    FakeCheckoutTestCase,
    VCSEntityFactory,
    VCSTranslationFactory,
)
from pontoon.sync.vcs.models import (
    MissingRepositoryPermalink,
    VCSConfiguration,
    VCSResource,
    VCSProject,
    DownloadTOMLParser,
)

TEST_CHECKOUT_PATH = os.path.join(
    os.path.dirname(__file__), "directory_detection_tests"
)


class VCSTestCase(TestCase):
    """
    Setup fixtures that are shared between VCS tests.
    """

    def setUp(self):
        self.get_project_config_patcher = patch(
            "pontoon.sync.vcs.models.DownloadTOMLParser.get_project_config"
        )
        self.get_project_config_mock = self.get_project_config_patcher.start()
        self.get_project_config_mock.side_effect = lambda config_path: os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH, config_path
        )
        self.addCleanup(self.get_project_config_patcher.stop)


class VCSProjectTests(VCSTestCase):
    def setUp(self):
        # Force the checkout path to point to a test directory to make
        # resource file loading pass during tests.
        checkout_path_patch = patch.object(
            Project,
            "checkout_path",
            new_callable=PropertyMock,
            return_value=os.path.join(TEST_CHECKOUT_PATH, "no_resources_test"),
        )
        self.mock_checkout_path = checkout_path_patch.start()
        self.addCleanup(checkout_path_patch.stop)

        self.locale = LocaleFactory.create(code="XY")
        self.project = ProjectFactory.create(
            locales=[self.locale],
            repositories__permalink="https://example.com/l10n/{locale_code}",
        )
        self.vcs_project = VCSProject(self.project)
        super(VCSProjectTests, self).setUp()

    @patch.object(VCSProject, "source_directory_path", new_callable=PropertyMock)
    def test_get_relevant_files_with_config(self, source_directory_path_mock):
        """
        Return relative reference paths and locales of paths found in project configuration.
        """
        source_directory_path_mock.return_value = ""
        paths = ["locale/path/to/localizable_file.ftl"]
        self.vcs_project.configuration = VCSConfiguration(self.vcs_project)

        # Return empty dict if no reference path found for any of the paths
        with patch(
            "pontoon.sync.vcs.models.VCSConfiguration.reference_path",
            return_value=None,
        ):
            files = self.vcs_project.get_relevant_files_with_config(paths)
            assert files == {}

        # Return empty dict if no reference path found for any of the paths
        with patch(
            "pontoon.sync.vcs.models.VCSConfiguration.reference_path",
            return_value="reference/path/to/localizable_file.ftl",
        ):
            files = self.vcs_project.get_relevant_files_with_config(paths)
            assert files == {"reference/path/to/localizable_file.ftl": [self.locale]}

    def test_get_relevant_files_without_config(self):
        """
        Return relative paths and their locales if they start with locale repository paths.
        """
        paths = [
            "locales/xy/path/to/localizable_file.ftl",
            "some.random.file",
            ".hidden_file",
        ]

        locale_path_locales = {
            "locales/ab": "AB",
            "locales/cd": "CD",
            "locales/xy": "XY",
        }

        files = self.vcs_project.get_relevant_files_without_config(
            paths, locale_path_locales
        )

        assert files == {"path/to/localizable_file.ftl": ["XY"]}

    def test_missing_permalink_prefix(self):
        """
        Fail when the source repository of a project with the project
        config doesn't have the permalink defined.
        """
        with self.assertRaises(MissingRepositoryPermalink):
            self.project.configuration_file = "l10n.toml"
            self.project.source_repository.permalink_prefix = ""
            self.project.source_repository.save()
            VCSProject(self.project,)

    def test_relative_resource_paths(self):
        with patch.object(
            VCSProject,
            "source_directory_path",
            new_callable=PropertyMock,
            return_value="/root/",
        ):
            self.vcs_project.resource_paths_without_config = Mock(
                return_value=["/root/foo.po", "/root/meh/bar.po"]
            )

            assert list(self.vcs_project.relative_resource_paths()) == [
                "foo.po",
                "meh/bar.po",
            ]

    def test_relative_resource_paths_pot(self):
        """
        If a resource ends in .pot, replace the extension with .po since
        relative paths are used within non-source locales that do not
        have .pot files.
        """
        with patch.object(
            VCSProject,
            "source_directory_path",
            new_callable=PropertyMock,
            return_value="/root/",
        ):
            self.vcs_project.resource_paths_without_config = Mock(
                return_value=["/root/foo.pot", "/root/meh/bar.pot"]
            )

            assert list(self.vcs_project.relative_resource_paths()) == [
                "foo.po",
                "meh/bar.po",
            ]

    def test_source_directory_with_config(self):
        """
        If project configuration provided, use source repository checkout path
        as source directory path.
        """
        self.vcs_project.configuration = Mock(return_value=[True])

        assert (
            self.vcs_project.source_directory_path
            == self.vcs_project.db_project.source_repository.checkout_path
        )

    def test_source_directory_path_no_resource(self):
        """
        When searching for source directories, do not match directories that
        do not contain resource files.
        """
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, "no_resources_test")
        self.mock_checkout_path.return_value = checkout_path

        assert self.vcs_project.source_directory_path == os.path.join(
            checkout_path, "real_resources", "templates"
        )

    def test_source_directory_scoring_templates(self):
        """
        When searching for source directories, prefer directories named
        `templates` over all others.
        """
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, "scoring_templates_test")
        self.mock_checkout_path.return_value = checkout_path

        assert self.vcs_project.source_directory_path == os.path.join(
            checkout_path, "templates"
        )

    def test_source_directory_scoring_en_US(self):
        """
        When searching for source directories, prefer directories named
        `en-US` over others besides `templates`.
        """
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, "scoring_en_US_test")
        self.mock_checkout_path.return_value = checkout_path

        assert self.vcs_project.source_directory_path == os.path.join(
            checkout_path, "en-US"
        )

    def test_source_directory_scoring_source_files(self):
        """
        When searching for source directories, prefer directories with
        source-only formats over all others.
        """
        checkout_path = os.path.join(TEST_CHECKOUT_PATH, "scoring_source_files_test")
        self.mock_checkout_path.return_value = checkout_path

        assert self.vcs_project.source_directory_path == os.path.join(
            checkout_path, "en"
        )  # en has pot files in it

    def test_resources_parse_error(self):
        """
        If VCSResource() raises a ParseError while loading, log an error
        and skip the resource.
        """
        self.vcs_project.relative_resource_paths = Mock(
            return_value=["failure", "success"]
        )

        # Fail only if the path is failure so we can test the ignore.
        def vcs_resource_constructor(project, path, locales=None):
            if path == "failure":
                raise ParseError("error message")
            else:
                return "successful resource"

        changed_vcs_resources = {"success": [], "failure": []}
        with patch("pontoon.sync.vcs.models.VCSResource") as MockVCSResource, patch(
            "pontoon.sync.vcs.models.log"
        ) as mock_log, patch.object(
            VCSProject,
            "changed_files",
            new_callable=PropertyMock,
            return_value=changed_vcs_resources,
        ):
            MockVCSResource.side_effect = vcs_resource_constructor

            assert self.vcs_project.resources == {"success": "successful resource"}
            mock_log.error.assert_called_with(CONTAINS("failure", "error message"))

    @patch.object(Repository, "checkout_path", new_callable=PropertyMock)
    def test_resource_paths_with_config(self, checkout_path_mock):
        """
        If project configuration provided, use it to collect absolute paths to all
        source resources within the source repository checkout path.
        """
        checkout_path_mock.return_value = PROJECT_CONFIG_CHECKOUT_PATH
        self.vcs_project.db_project.configuration_file = "l10n.toml"
        self.vcs_project.configuration = VCSConfiguration(self.vcs_project)

        assert sorted(list(self.vcs_project.resource_paths_with_config())) == sorted(
            [
                os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, "values/amo.pot"),
                os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, "values/strings.properties"),
                os.path.join(
                    PROJECT_CONFIG_CHECKOUT_PATH, "values/strings_child.properties"
                ),
                os.path.join(
                    PROJECT_CONFIG_CHECKOUT_PATH, "values/strings_reality.properties",
                ),
            ]
        )

    @patch.object(VCSProject, "source_directory_path", new_callable=PropertyMock)
    def test_resource_paths_without_config_region_properties(
        self, source_directory_path_mock
    ):
        """
        If a project has a repository_url in pontoon.base.MOZILLA_REPOS,
        resource_paths_without_config should ignore files named
        "region.properties".
        """
        source_directory_path_mock.return_value = "/root"
        url = "https://moz.example.com"
        self.project.repositories.all().delete()
        self.project.repositories.add(RepositoryFactory.create(url=url))

        with patch(
            "pontoon.sync.vcs.models.scandir", wraps=scandir
        ) as mock_scandir, patch("pontoon.sync.vcs.models.MOZILLA_REPOS", [url]):
            mock_scandir.walk.return_value = [
                ("/root", [], ["foo.pot", "region.properties"])
            ]

            assert list(self.vcs_project.resource_paths_without_config()) == [
                os.path.join("/root", "foo.pot")
            ]

    @patch.object(VCSProject, "source_directory_path", new_callable=PropertyMock)
    def test_resource_paths_without_config_exclude_hidden(
        self, source_directory_path_mock
    ):
        """
        We should filter out resources that are contained in the hidden paths.
        """
        source_directory_path_mock.return_value = "/root"
        hidden_paths = (
            ("/root/.hidden_folder/templates", [], ("bar.pot",)),
            ("/root/templates", [], ("foo.pot",)),
        )
        with patch(
            "pontoon.sync.vcs.models.scandir.walk",
            wraps=scandir,
            return_value=hidden_paths,
        ):
            assert list(self.vcs_project.resource_paths_without_config()) == [
                "/root/templates/foo.pot"
            ]


class VCSConfigurationTests(VCSTestCase):
    toml = "l10n.toml"

    def setUp(self):
        super(VCSConfigurationTests, self).setUp()
        self.locale, _ = Locale.objects.get_or_create(code="fr")

        self.repository = RepositoryFactory()
        self.db_project = ProjectFactory.create(repositories=[self.repository],)

        checkout_path_patch = patch.object(
            Repository,
            "checkout_path",
            new_callable=PropertyMock,
            return_value=PROJECT_CONFIG_CHECKOUT_PATH,
        )
        self.mock_checkout_path = checkout_path_patch.start()
        self.addCleanup(checkout_path_patch.stop)

        self.resource_amo = ResourceFactory.create(
            project=self.db_project, path="values/amo.pot",
        )
        self.resource_strings = ResourceFactory.create(
            project=self.db_project, path="values/strings.properties",
        )
        self.resource_strings_reality = ResourceFactory.create(
            project=self.db_project, path="values/strings_reality.properties",
        )
        self.resource_strings_child = ResourceFactory.create(
            project=self.db_project, path="values/strings_child.properties",
        )

        # Make sure VCSConfiguration instance is initialized
        self.db_project.configuration_file = self.toml
        self.db_project.source_repository.permalink_prefix = "https://example.com/"
        self.vcs_project = VCSProject(self.db_project, locales=[self.locale])

    def test_add_locale(self):
        config = self.vcs_project.configuration.parsed_configuration
        locale_code = "new-locale-code"

        assert locale_code not in config.all_locales

        self.vcs_project.configuration.add_locale(locale_code)

        assert locale_code in config.locales

    def test_get_or_set_project_files_reference(self):
        self.vcs_project.configuration.add_locale = Mock()
        locale_code = None

        assert (
            self.vcs_project.configuration.get_or_set_project_files(locale_code,).locale
            == locale_code
        )

        assert not self.vcs_project.configuration.add_locale.called

    def test_get_or_set_project_files_l10n(self):
        self.vcs_project.configuration.add_locale = Mock()
        locale_code = self.locale.code

        assert (
            self.vcs_project.configuration.get_or_set_project_files(locale_code,).locale
            == locale_code
        )

        assert not self.vcs_project.configuration.add_locale.called

    def test_get_or_set_project_files_new_locale(self):
        self.vcs_project.configuration.add_locale = Mock()
        locale_code = "new-locale-code"

        assert (
            self.vcs_project.configuration.get_or_set_project_files(locale_code,).locale
            == locale_code
        )

        assert self.vcs_project.configuration.add_locale.called

    def test_l10n_path(self):
        absolute_resource_path = os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH, "values/amo.pot",
        )

        l10n_path = os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, "values-fr/amo.po",)

        assert (
            self.vcs_project.configuration.l10n_path(
                self.locale, absolute_resource_path,
            )
            == l10n_path
        )

    def test_reference_path(self):
        absolute_l10n_path = os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH, "values-fr/amo.po",
        )

        reference_path = os.path.join(PROJECT_CONFIG_CHECKOUT_PATH, "values/amo.pot",)

        assert (
            self.vcs_project.configuration.reference_path(
                self.locale, absolute_l10n_path,
            )
            == reference_path
        )

    def test_locale_resources(self):
        assert sorted(
            self.vcs_project.configuration.locale_resources(self.locale),
            key=lambda r: r.path,
        ) == [
            self.resource_amo,
            self.resource_strings,
            self.resource_strings_child,
            self.resource_strings_reality,
        ]


class GrandFatheredVCSConfigurationTest(VCSConfigurationTests):
    """Testing with deep includes and excludes"""

    toml = "grandfather.toml"

    def test_locale_resources(self):
        # no resource_strings, excluded for `fr`
        assert sorted(
            self.vcs_project.configuration.locale_resources(self.locale),
            key=lambda r: r.path,
        ) == [
            self.resource_amo,
            # self.resource_strings,
            self.resource_strings_child,
            self.resource_strings_reality,
        ]


def setUpResource(self):
    self.repository = RepositoryFactory()
    self.db_project = ProjectFactory.create(repositories=[self.repository],)

    checkout_path_patch = patch.object(
        Repository,
        "checkout_path",
        new_callable=PropertyMock,
        return_value=PROJECT_CONFIG_CHECKOUT_PATH,
    )
    self.mock_checkout_path = checkout_path_patch.start()
    self.addCleanup(checkout_path_patch.stop)

    # Make sure VCSConfiguration instance is initialized
    self.db_project.configuration_file = "l10n.toml"

    self.db_project.source_repository.permalink_prefix = "https://example.com/"
    self.vcs_project = VCSProject(self.db_project, locales=[self.locale])


class VCSConfigurationFullLocaleTests(VCSTestCase):
    def setUp(self):
        self.locale, _ = Locale.objects.get_or_create(code="fr")
        setUpResource(self)
        super(VCSConfigurationFullLocaleTests, self).setUp()

    def test_vcs_resource(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, "values/strings.properties", [self.locale])
        assert r.files[self.locale].path == os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH, "values-fr/strings.properties"
        )

    def test_vcs_resource_path(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(
            self.vcs_project, "values/strings_reality.properties", [self.locale]
        )
        assert r.files[self.locale].path == os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH, "values-fr/strings_reality.properties"
        )

    def test_vcs_resource_child(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(
            self.vcs_project, "values/strings_child.properties", [self.locale]
        )
        assert r.files[self.locale].path == os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH, "values-fr/strings_child.properties"
        )


class VCSConfigurationPartialLocaleTests(VCSTestCase):
    def setUp(self):
        self.locale, _ = Locale.objects.get_or_create(code="sl")
        setUpResource(self)
        super(VCSConfigurationPartialLocaleTests, self).setUp()

    def test_vcs_resource(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(self.vcs_project, "values/strings.properties", [self.locale])
        assert r.files[self.locale].path == os.path.join(
            PROJECT_CONFIG_CHECKOUT_PATH, "values-sl/strings.properties"
        )

    def test_vcs_resource_path(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(
            self.vcs_project, "values/strings_reality.properties", [self.locale]
        )
        assert r.files == {}

    def test_vcs_resource_child(self):
        self.vcs_project.configuration.add_locale(self.locale.code)
        r = VCSResource(
            self.vcs_project, "values/strings_child.properties", [self.locale]
        )
        assert r.files == {}


class VCSEntityTests(VCSTestCase):
    def test_has_translation_for(self):
        """
        Return True if a translation exists for the given locale, even
        if the translation is empty/falsey.
        """
        empty_translation = VCSTranslationFactory(strings={})
        full_translation = VCSTranslationFactory(strings={None: "TRANSLATED"})
        entity = VCSEntityFactory()
        entity.translations = {"empty": empty_translation, "full": full_translation}

        assert not entity.has_translation_for("missing")
        assert entity.has_translation_for("empty")
        assert entity.has_translation_for("full")


class VCSChangedConfigFilesTests(FakeCheckoutTestCase):
    """
    Tests the algorithm that detects changes of Project Config files.
    """

    def test_no_config_changes(self):
        changed_source_files = {"file1.po": [], "test.toml": []}

        with patch.object(
            self.vcs_project, "configuration"
        ) as changed_config_files_mock, patch.object(
            self.vcs_project, "changed_source_files", return_value=changed_source_files
        ) as changed_source_files_mock:
            changed_config_files_mock.parsed_configuration.configs.__iter__.return_value = (
                set()
            )
            changed_source_files_mock.__getitem__.return_value = changed_source_files
            self.assertSetEqual(self.vcs_project.changed_config_files, set())

    def test_changed_config_files(self):
        config_file_mock = MagicMock()
        config_file_mock.path = str(
            Path(self.vcs_project.source_directory_path).joinpath(
                Path("test-l10n.toml")
            )
        )
        changed_config_files = [config_file_mock]
        changed_source_files = {
            "file1.po": [],
            "test-l10n.toml": [],
        }

        with patch.object(
            self.vcs_project, "configuration"
        ) as changed_config_files_mock, patch.object(
            self.vcs_project, "changed_source_files", return_value=changed_source_files
        ) as changed_source_files_mock:
            changed_config_files_mock.parsed_configuration.configs.__iter__.return_value = (
                changed_config_files
            )
            changed_source_files_mock.__getitem__.return_value = changed_source_files

            self.assertSetEqual(
                self.vcs_project.changed_config_files, {"test-l10n.toml"}
            )


class DownloadTOMLParserTests(TestCase):
    def setUp(self):
        self.requests_patcher = patch("pontoon.sync.vcs.models.requests.get")
        self.requests_mock = self.requests_patcher.start()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        self.requests_patcher.stop()

    def test_config_file_not_found(self):
        """
        When the project config file is not available, throw an error.
        """
        self.requests_mock.return_value.raise_for_status.side_effect = HTTPException(
            "not found"
        )

        with self.assertRaises(HTTPException):
            parser = DownloadTOMLParser(
                self.temp_dir, "https://example.com/", "l10n.toml"
            )
            parser.parse()

    def test_remote_path(self):
        parser = DownloadTOMLParser(
            "", "https://example.com/without-locale-code/", "l10n.toml"
        )
        self.assertEqual(
            parser.get_remote_path("l10n.toml"),
            "https://example.com/without-locale-code/l10n.toml",
        )
        self.assertEqual(
            parser.get_remote_path("subdir/l10n.toml"),
            "https://example.com/without-locale-code/subdir/l10n.toml",
        )

    def test_local_path(self):
        parser = DownloadTOMLParser(self.temp_dir, "", "aaa.toml")
        self.assertEqual(parser.get_local_path("aaa.toml"), f"{self.temp_dir}/aaa.toml")

    def test_get_project_config(self):
        parser = DownloadTOMLParser(self.temp_dir, "https://example.com/", "l10n.toml")
        self.requests_mock.return_value.content = b"test-content"
        project_config_path = parser.get_project_config("l10n.toml")

        self.assertTrue(self.requests_mock.called)
        self.assertEqual(project_config_path, self.temp_dir + "/l10n.toml")
        self.assertEqual(open(project_config_path, "r").read(), "test-content")
