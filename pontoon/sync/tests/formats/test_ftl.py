import os
import shutil
import tempfile

from textwrap import dedent

import pytest
from pontoon.base.tests import (
    assert_attributes_equal,
    create_named_tempfile,
    LocaleFactory,
    TestCase,
)
from pontoon.sync.exceptions import ParseError
from pontoon.sync.formats import ftl
from pontoon.sync.tests.formats import FormatTestsMixin


class FTLResourceTests(FormatTestsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tempdir)

    def get_nonexistant_file_resource(self, path):
        contents = "text = Arise, awake and do not stop until the goal is reached."

        source_path = create_named_tempfile(
            contents, prefix="strings", suffix=".ftl", directory=self.tempdir,
        )
        source_resource = ftl.FTLResource(
            path=source_path, locale=None, source_resource=None
        )

        return ftl.FTLResource(path, locale=None, source_resource=source_resource,)

    def get_nonexistant_file_path(self):
        return os.path.join(self.tempdir, "strings.ftl")

    def test_init_missing_resource(self):
        """
        If the FTLResource file doesn't exist and no source resource is
        given, raise a ParseError.
        """
        path = self.get_nonexistant_file_path()
        with pytest.raises(ParseError):
            ftl.FTLResource(path, locale=None, source_resource=None)

    def test_init_missing_resource_with_source(self):
        """
        If the FTLResource doesn't exist but a source resource is
        given, return a resource with empty translations.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path)

        assert len(translated_resource.translations) == 1
        assert translated_resource.translations[0].strings == {}

    def test_save_create_dirs(self):
        """
        If the directories in a resource's path don't exist, create them on
        save.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path)

        translated_resource.translations[0].strings = {None: "New Translated String"}

        assert not os.path.exists(path)
        translated_resource.save(LocaleFactory.create())
        assert os.path.exists(path)

    def test_parse_with_source_path(self):
        contents = "text = Arise, awake and do not stop until the goal is reached."
        source_path = create_named_tempfile(
            contents, prefix="strings", suffix=".ftl", directory=self.tempdir,
        )
        path = self.get_nonexistant_file_path()
        obj = ftl.parse(path, source_path=source_path, locale=None)
        assert obj.path == path
        assert obj.locale is None
        assert obj.source_resource.path == source_path
        assert obj.source_resource.locale is None

    def test_parse_with_no_source_path(self):
        contents = "text = Arise, awake and do not stop until the goal is reached."
        path = create_named_tempfile(
            contents, prefix="strings", suffix=".ftl", directory=self.tempdir,
        )
        obj = ftl.parse(path, source_path=None, locale=None)
        assert obj.path == path
        assert obj.source_resource is None
        assert obj.locale is None


BASE_FTL_FILE = """
# Sample comment
SourceString = Translated String

# First comment
# Second comment
MultipleComments = Translated Multiple Comments

NoCommentsOrSources = Translated No Comments or Sources
"""


class FTLTests(FormatTestsMixin, TestCase):
    parse = staticmethod(ftl.parse)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tempdir)

    def key(self, source_string):
        """FTL keys can't contain spaces."""
        return super().key(source_string).replace(" ", "")

    def test_parse_basic(self):
        input_string = BASE_FTL_FILE
        translation_index = 0
        path, resource = self.parse_string(input_string)

        assert_attributes_equal(
            resource.translations[translation_index],
            comments=["Sample comment"],
            key=self.key("Source String"),
            strings={None: "SourceString = Translated String\n"},
            fuzzy=False,
            order=translation_index,
        )

    def test_parse_multiple_comments(self):
        input_string = BASE_FTL_FILE
        translation_index = 1
        path, resource = self.parse_string(input_string)

        assert_attributes_equal(
            resource.translations[translation_index],
            comments=["First comment\nSecond comment"],
            source=[],
            key=self.key("Multiple Comments"),
            strings={None: "MultipleComments = Translated Multiple Comments\n"},
            fuzzy=False,
            order=translation_index,
        )

    def test_parse_no_comments_no_sources(self):
        input_string = BASE_FTL_FILE
        translation_index = 2
        path, resource = self.parse_string(input_string)

        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key("No Comments Or Sources"),
            strings={None: "NoCommentsOrSources = Translated No Comments or Sources\n"},
            fuzzy=False,
            order=translation_index,
        )

    def test_save_basic(self):
        input_string = "SourceString = Source String"
        expected_translation = "SourceString = New Translated String"
        expected_string = "{expected_translation}".format(
            expected_translation=expected_translation
        )

        self.run_save_basic(
            input_string,
            expected_string,
            source_string=input_string,
            expected_translation=expected_translation,
        )

    def test_save_remove(self):
        """Deleting strings removes them completely from the FTL file."""
        input_string = "Source-String = Source String"
        expected_string = ""

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent(
            """
            SourceString = Source String
        """
        )
        input_string = dedent(
            """
            MissingSourceString = Translated Missing String
            SourceString = Translated String
        """
        )
        expected_string = dedent(
            """
            SourceString = Translated String
        """
        )

        self.run_save_no_changes(
            input_string, expected_string, source_string=source_string
        )

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent(
            """
            SourceString = Source String
            OtherSourceString = Other String
        """
        )
        input_string = dedent(
            """
            OtherSourceString = Translated Other String
        """
        )

        self.run_save_no_changes(
            input_string, input_string, source_string=source_string
        )

    def test_save_translation_missing(self):
        source_string = dedent(
            """
            String = Source String
            MissingString = Missing Source String
        """
        )
        input_string = dedent(
            """
            String = Translated String
        """
        )
        expected_translation = "MissingString = New Translated String"
        expected_string = dedent(
            """
            String = Translated String
            {expected_translation}
        """.format(
                expected_translation=expected_translation
            )
        )

        self.run_save_translation_missing(
            source_string,
            input_string,
            expected_string,
            expected_translation=expected_translation,
        )

    def test_save_translation_identical(self):
        source_string = "String = Source String"
        input_string = "String = Translated String"
        expected_translation = "String = Source String"
        expected_string = "{expected_translation}".format(
            expected_translation=expected_translation
        )

        self.run_save_translation_identical(
            source_string,
            input_string,
            expected_string,
            expected_translation=expected_translation,
        )
