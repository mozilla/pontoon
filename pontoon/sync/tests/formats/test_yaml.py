import os
import shutil
import tempfile

from textwrap import dedent

import pytest

from pontoon.base.tests import (
    LocaleFactory,
    TestCase,
    assert_attributes_equal,
    create_named_tempfile,
)
from pontoon.sync.formats import yaml_keyvalue
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.tests.formats import FormatTestsMixin

nested_file = """
    key1:
        key2: value2
"""

class YAMLResourceTests(TestCase):
    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tempdir)

    def get_invalid_file_path(self):
        return os.path.join(self.tempdir, "invalid.yaml")

    def get_nonexistant_file_path(self):
        return os.path.join(self.tempdir, "strings.yaml")

    def get_nonexistant_file_resource(self, path, contents=""):
        source_path = create_named_tempfile(
            contents,
            prefix="strings",
            suffix=".yaml",
            directory=self.tempdir,
        )
        source_resource = yaml_keyvalue.YAMLResource(source_path)

        return yaml_keyvalue.YAMLResource(
            path,
            source_resource=source_resource,
        )

    def get_file_resource(self, contents = ""):
        source_path = create_named_tempfile(
            contents,
            prefix="strings",
            suffix=".yaml",
            directory=self.tempdir,
        )

        return yaml_keyvalue.YAMLResource(source_path)

    def test_init_missing_resource(self):
        """
        If the translated resource doesn't exist and no source resource is
        given, raise a ParseError.
        """
        path = self.get_nonexistant_file_path()
        with pytest.raises(ParseError):
            yaml_keyvalue.YAMLResource(path, source_resource=None)

    def test_init_missing_resource_with_empty_source(self):
        """
        If the translated resource doesn't exist but a source resource is
        given, return a resource no translations
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path)

        assert len(translated_resource.translations) == 0

    def test_init_missing_resource_with_some_source(self):
        """
        If the translated resource doesn't exist but a source resource is
        given, return a resource with empty translations.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path, dedent("""
            key: value
        """))

        assert len(translated_resource.translations) == 1
        assert translated_resource.translations[0].strings == {}

    def test_read_resource_from_file(self):
        """
        If the translated resource exists, sets all the keys
        """
        translated_resource = self.get_file_resource(dedent(
            """
                key1: value1
                key2: value2
            """
        ))

        assert len(translated_resource.translations) == 2
        assert translated_resource.translations[0].strings[None] == 'value1'
        assert translated_resource.translations[0].key == 'key1'

        assert translated_resource.translations[1].strings[None] == 'value2'
        assert translated_resource.translations[1].key == 'key2'

    def test_read_resource_from_file_nested(self):
        """
        If the translated resource exist, sets all the nested keys
        """
        translated_resource = self.get_file_resource(nested_file)

        assert len(translated_resource.translations) == 1
        assert translated_resource.translations[0].strings[None] == 'value2'
        assert translated_resource.translations[0].key == 'key1.key2'

    def test_save_create_dirs(self):
        """
        If the directories in a resource's path don't exist, create them on
        save.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path, dedent("""
            key: value
        """))

        translated_resource.translations[0].strings = {None: "New Translated String"}

        assert not os.path.exists(path)
        translated_resource.save(LocaleFactory.create())
        assert os.path.exists(path)

    def test_save_file_no_changes(self):
        """
        Saving a file without changes results in the same file
        """
        file_content = "key1: value1\nkey2: value2\n"

        translated_resource = self.get_file_resource(file_content)
        translated_resource.save(LocaleFactory.create())

        result = open(translated_resource.path, 'r').read()

        assert result == file_content

    def test_save_file_with_changes(self):
        """
        Saving a file without changes results in the same file
        """
        file_content = "key1: value1\nkey2: value2\n"

        translated_resource = self.get_file_resource(file_content)
        translated_resource.translations[0].strings = {None: "New Translated String"}
        translated_resource.save(LocaleFactory.create())

        result = open(translated_resource.path, 'r').read()

        assert result == "key1: New Translated String\nkey2: value2\n"

    def test_save_file_nested_changes(self):
        """
        Saving a file without changes results in the same file
        """
        file_content = "key1: value1\nkey2: value2\n"

        translated_resource = self.get_file_resource(file_content)
        translated_resource.translations[0].key = "a.b.c"
        translated_resource.save(LocaleFactory.create())

        result = open(translated_resource.path, 'r').read()

        assert result == "key2: value2\na:\n  b:\n    c: value1\n"
