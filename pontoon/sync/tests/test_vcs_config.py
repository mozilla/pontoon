import tempfile
from http.client import HTTPException
from unittest.mock import patch

from pontoon.base.tests import TestCase
from pontoon.sync.vcs.config import DownloadTOMLParser


class DownloadTOMLParserTests(TestCase):
    def setUp(self):
        self.requests_patcher = patch("pontoon.sync.vcs.config.requests.get")
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
        self.assertEqual(open(project_config_path).read(), "test-content")
