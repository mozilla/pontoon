from typing import Any

from pontoon.base.tests import (
    LocaleFactory,
    assert_attributes_equal,
    create_tempfile,
)


class FormatTestsMixin:
    """
    Mixin for tests and methods that are common to all supported
    formats.

    Each format we support should have a test class that subclasses this
    class and overrides the tests for features that it supports. If a
    format doesn't support a particular feature, don't override the
    test method for that feature and it won't be run.
    """

    maxDiff: Any = None

    # Subclasses should override the following attributes to customize
    # how these tests are run.

    # Parse function for the format we're testing.
    parse = None

    # Supports keys that are separate from source strings.
    supports_keys = False

    # Supports source (the filename and line where a translation is
    # located).
    supports_source = False

    # Supports source strings in translated resource. Asymmetric formats
    # do not support this.
    supports_source_string = False

    def setUp(self):
        super().setUp()
        self.locale = LocaleFactory.create(
            code="test-locale",
            name="Test Locale",
            plural_rule="(n != 1)",
            cldr_plurals="1,5",
        )

    def parse_string(
        self,
        string,
        source_string=None,
        locale=None,
        path=None,
        source_path=None,
    ):
        path = path or create_tempfile(string)
        locale = locale or self.locale
        if source_string is not None:
            source_path = source_path or create_tempfile(source_string)
            return path, self.parse(path, source_path=source_path, locale=locale)
        else:
            return path, self.parse(path, locale=locale)

    def key(self, source_string):
        """
        Return the expected key for an entity with the given source
        string based on whether the format we're testing supports unique
        keys or not.
        """
        return source_string if not self.supports_keys else source_string + " Key"

    # Parse tests assume that they're running off of a common
    # translation file, passed in as the first argument. The second
    # argument is the index of the entity used for that test.

    def run_parse_basic(self, input_string, translation_index):
        """Basic translation with a comment and source."""
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=["Sample comment"],
            key=self.key("Source String"),
            strings={None: "Translated String"},
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source:
            assert resource.translations[translation_index].source == [("file.py", "1")]

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Source String",
                source_string_plural="",
            )

    def run_parse_multiple_comments(
        self,
        input_string,
        translation_index,
        comments=None,
    ):
        path, resource = self.parse_string(input_string)

        if comments is None:
            comments = ["First comment", "Second comment"]

        assert_attributes_equal(
            resource.translations[translation_index],
            comments=comments,
            source=[],
            key=self.key("Multiple Comments"),
            strings={None: "Translated Multiple Comments"},
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Multiple Comments",
                source_string_plural="",
            )

    def run_parse_multiple_sources(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[("file.py", "2"), ("file.py", "3")],
            key=self.key("Multiple Sources"),
            strings={None: "Translated Multiple Sources"},
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Multiple Sources",
                source_string_plural="",
            )

    def run_parse_fuzzy(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key("Fuzzy"),
            strings={None: "Translated Fuzzy"},
            fuzzy=True,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Fuzzy",
                source_string_plural="",
            )

    def run_parse_no_comments_no_sources(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key("No Comments or Sources"),
            strings={None: "Translated No Comments or Sources"},
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="No Comments or Sources",
                source_string_plural="",
            )

    def run_parse_missing_translation(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key("Missing Translation"),
            strings={},
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Missing Translation",
                source_string_plural="",
            )

    def run_parse_plural_translation(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key("Plural %(count)s string"),
            strings={
                0: "Translated Plural %(count)s string",
                1: "Translated Plural %(count)s strings",
            },
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Plural %(count)s string",
                source_string_plural="Plural %(count)s strings",
            )

    def run_parse_plural_translation_missing(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key("Plural %(count)s string with missing translations"),
            strings={
                1: "Translated Plural %(count)s strings with missing translations"
            },
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Plural %(count)s string with missing translations",
                source_string_plural="Plural %(count)s strings with missing translations",
            )

    def run_parse_empty_translation(self, input_string, translation_index):
        """Test that empty translations are parsed properly."""
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key("Empty Translation"),
            strings={None: ""},
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source_string:
            assert_attributes_equal(
                resource.translations[translation_index],
                source_string="Empty Translation",
            )

    def assert_file_content(self, file_path, expected_content, strip=True):
        with open(file_path) as f:
            actual_content = f.read()

            # Strip leading and trailing whitespace by default as we
            # normally don't care about this.
            if strip:
                actual_content = actual_content.strip()
                expected_content = expected_content.strip()

            self.assertMultiLineEqual(actual_content, expected_content)
