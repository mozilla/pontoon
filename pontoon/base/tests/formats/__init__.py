import os
import tempfile

from django_nose.tools import assert_equal

from pontoon.base.tests import (
    assert_attributes_equal,
    LocaleFactory,
)


class FormatTestsMixin(object):
    """
    Mixin for tests and methods that are common to all supported
    formats.

    Each format we support should have a test class that subclasses this
    class and overrides the tests for features that it supports. If a
    format doesn't support a particular feature, don't override the
    test method for that feature and it won't be run.
    """
    maxDiff = None

    # Subclasses should override the following attributes to customize
    # how these tests are run.

    # Parse function for the format we're testing.
    parse = None

    # Supports keys that are separate from source strings.
    supports_keys = False

    # Supports source (the filename and line where a translation is
    # located).
    supports_source = False

    def setUp(self):
        super(FormatTestsMixin, self).setUp()
        self.locale = LocaleFactory.create(
            code='test-locale',
            name='Test Locale',
            plural_rule='(n != 1)',
            cldr_plurals='1,5',
        )

    def parse_string(self, string):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as f:
            f.write(string)

        return path, self.parse(path)

    def key(self, source_string):
        """
        Return the expected key for an entity with the given source
        string based on whether the format we're testing supports unique
        keys or not.
        """
        return source_string if not self.supports_keys else source_string + ' Key'

    # Parse tests assume that they're running off of a common
    # translation file, passed in as the first argument. The second
    # argument is the index of the entity used for that test.

    def run_parse_basic(self, input_string, translation_index):
        """Basic translation with a comment and source."""
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[0],
            comments=['Sample comment'],
            key=self.key('Source String'),
            source_string='Source String',
            source_string_plural='',
            strings={None: 'Translated String'},
            fuzzy=False,
            order=translation_index,
        )

        if self.supports_source:
            assert_equal(resource.translations[0].source, [('file.py', '1')])

    def run_parse_multiple_comments(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=['First comment', 'Second comment'],
            source=[],
            key=self.key('Multiple Comments'),
            source_string='Multiple Comments',
            source_string_plural='',
            strings={None: 'Translated Multiple Comments'},
            fuzzy=False,
            order=translation_index,
        )

    def run_parse_multiple_sources(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[('file.py', '2'), ('file.py', '3')],
            key=self.key('Multiple Sources'),
            source_string='Multiple Sources',
            source_string_plural='',
            strings={None: 'Translated Multiple Sources'},
            fuzzy=False,
            order=translation_index,
        )

    def run_parse_fuzzy(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key('Fuzzy'),
            source_string='Fuzzy',
            source_string_plural='',
            strings={None: 'Translated Fuzzy'},
            fuzzy=True,
            order=translation_index,
        )

    def run_parse_no_comments_no_sources(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key('No Comments or Sources'),
            source_string='No Comments or Sources',
            source_string_plural='',
            strings={None: 'Translated No Comments or Sources'},
            fuzzy=False,
            order=translation_index,
        )

    def run_parse_missing_traslation(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key('Missing Translation'),
            source_string='Missing Translation',
            source_string_plural='',
            strings={},
            fuzzy=False,
            order=translation_index,
        )

    def run_parse_plural_translation(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key('Plural %(count)s string'),
            source_string='Plural %(count)s string',
            source_string_plural='Plural %(count)s strings',
            strings={
                0: 'Translated Plural %(count)s string',
                1: 'Translated Plural %(count)s strings'
            },
            fuzzy=False,
            order=translation_index,
        )

    def run_parse_plural_translation_missing(self, input_string, translation_index):
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=[],
            source=[],
            key=self.key('Plural %(count)s string with missing translations'),
            source_string='Plural %(count)s string with missing translations',
            source_string_plural='Plural %(count)s strings with missing translations',
            strings={
                1: 'Translated Plural %(count)s strings with missing translations'
            },
            fuzzy=False,
            order=translation_index,
        )

    def assert_file_content(self, file_path, expected_content):
        with open(file_path) as f:
            self.assertMultiLineEqual(f.read(), expected_content)

    # Save tests take in an input and expected string that contain the
    # state of the translation file before and after the change being
    # tested is made to the parsed resource and saved.

    def run_save_basic(self, input_string, expected_string):
        """
        Test saving changes to an entity with a single translation.
        """
        path, resource = self.parse_string(input_string)

        translation = resource.translations[0]
        translation.strings[None] = 'New Translated String'
        translation.fuzzy = True
        resource.save(self.locale)

        self.assert_file_content(path, expected_string)

    def run_save_remove(self, input_string, expected_string):
        """Test saving a removed entity with a single translation."""
        path, resource = self.parse_string(input_string)

        translation = resource.translations[0]
        translation.strings = {}
        resource.save(self.locale)

        self.assert_file_content(path, expected_string)

    def run_save_plural(self, input_string, expected_string):
        path, resource = self.parse_string(input_string)

        translation = resource.translations[0]
        translation.strings[0] = 'New Plural'
        translation.strings[1] = 'New Plurals'
        resource.save(self.locale)

        self.assert_file_content(path, expected_string)

    def run_save_plural_remove(self, input_string, expected_string):
        """
        Any missing plurals should be set to an empty string in the
        pofile.
        """
        path, resource = self.parse_string(input_string)

        translation = resource.translations[0]
        translation.strings[0] = 'New Plural'
        del translation.strings[1]
        resource.save(self.locale)

        self.assert_file_content(path, expected_string)

    def run_save_remove_fuzzy(self, input_string, expected_string):
        path, resource = self.parse_string(input_string)

        resource.translations[0].fuzzy = False
        resource.save(self.locale)

        self.assert_file_content(path, expected_string)
