import os
import tempfile
from datetime import datetime
from textwrap import dedent

from pontoon.base.formats import po
from pontoon.base.tests import (
    assert_attributes_equal,
    LocaleFactory,
    TestCase,
    UserFactory
)


BASE_POFILE = """
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2015-08-04 12:30+0000\n"
"PO-Revision-Date: 2015-08-17 09:19:54+0000\n"
"Last-Translator: mkelly <mkelly@mozilla.com>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: zh_CN\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\n"
"Generated-By: Babel 0.9.5\n"
"X-Generator: Pontoon\n"

#. Sample comment
#: file.py:1
msgid "Source String"
msgstr "Translated String"

#. First comment
#. Second comment
msgid "Multiple Comments"
msgstr "Translated Multiple Comments"

#: file.py:2
#: file.py:3
msgid "Multiple Sources"
msgstr "Translated Multiple Sources"

#, fuzzy
msgid "Fuzzy"
msgstr "Translated Fuzzy"

msgid "No Comments or Sources"
msgstr "Translated No Comments or Sources"

msgid "Missing Translation"
msgstr ""

msgid "Plural %(count)s string"
msgid_plural "Plural %(count)s strings"
msgstr[0] "Translated Plural %(count)s string"
msgstr[1] "Translated Plural %(count)s strings"

msgid "Plural %(count)s string with missing translations"
msgid_plural "Plural %(count)s strings with missing translations"
msgstr[0] ""
msgstr[1] "Translated Plural %(count)s strings with missing translations"
"""

HEADER_TEMPLATE = """#\x20
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2015-08-04 12:30+0000\\n"
"PO-Revision-Date: {revision_date}\\n"
"Last-Translator: {last_translator}\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: {language}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: {plural_forms}\\n"
"Generated-By: Babel 0.9.5\\n"
"X-Generator: {generator}\\n"
"""


class POTests(TestCase):
    maxDiff = None

    def setUp(self):
        self.locale = LocaleFactory.create(
            code='test-locale',
            name='Test Locale',
            nplurals=2,
            plural_rule='(n != 1)',
        )

    def parse_string(self, string):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as f:
            f.write(string)

        return path, po.parse(path)

    def test_parse_basic(self):
        """Basic translation with a comment and source."""
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[0],
            comments=['Sample comment'],
            source=[('file.py', '1')],
            key='Source String',
            source_string='Source String',
            source_string_plural='',
            strings={None: 'Translated String'},
            fuzzy=False,
            order=0,
        )

    def test_parse_multiple_comments(self):
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[1],
            comments=['First comment', 'Second comment'],
            source=[],
            key='Multiple Comments',
            source_string='Multiple Comments',
            source_string_plural='',
            strings={None: 'Translated Multiple Comments'},
            fuzzy=False,
            order=1,
        )

    def test_parse_multiple_sources(self):
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[2],
            comments=[],
            source=[('file.py', '2'), ('file.py', '3')],
            key='Multiple Sources',
            source_string='Multiple Sources',
            source_string_plural='',
            strings={None: 'Translated Multiple Sources'},
            fuzzy=False,
            order=2,
        )

    def test_parse_fuzzy(self):
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[3],
            comments=[],
            source=[],
            key='Fuzzy',
            source_string='Fuzzy',
            source_string_plural='',
            strings={None: 'Translated Fuzzy'},
            fuzzy=True,
            order=3,
        )

    def test_parse_no_comments_no_sources(self):
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[4],
            comments=[],
            source=[],
            key='No Comments or Sources',
            source_string='No Comments or Sources',
            source_string_plural='',
            strings={None: 'Translated No Comments or Sources'},
            fuzzy=False,
            order=4,
        )

    def test_parse_missing_traslation(self):
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[5],
            comments=[],
            source=[],
            key='Missing Translation',
            source_string='Missing Translation',
            source_string_plural='',
            strings={},
            fuzzy=False,
            order=5,
        )

    def test_parse_plural_translation(self):
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[6],
            comments=[],
            source=[],
            key='Plural %(count)s string',
            source_string='Plural %(count)s string',
            source_string_plural='Plural %(count)s strings',
            strings={
                0: 'Translated Plural %(count)s string',
                1: 'Translated Plural %(count)s strings'
            },
            fuzzy=False,
            order=6,
        )

    def test_parse_plural_translation_missing(self):
        path, resource = self.parse_string(BASE_POFILE)
        assert_attributes_equal(
            resource.translations[7],
            comments=[],
            source=[],
            key='Plural %(count)s string with missing translations',
            source_string='Plural %(count)s string with missing translations',
            source_string_plural='Plural %(count)s strings with missing translations',
            strings={
                1: 'Translated Plural %(count)s strings with missing translations'
            },
            fuzzy=False,
            order=7,
        )

    def generate_pofile(
        self, body,
        revision_date='2015-08-04 12:30+0000',
        last_translator='example <example@example.com>',
        language='test_locale',
        plural_forms='nplurals=2; plural=(n != 1);',
        generator='Pontoon'
    ):
        header = HEADER_TEMPLATE.format(
            revision_date=revision_date,
            last_translator=last_translator,
            language=language,
            plural_forms=plural_forms,
            generator=generator
        )
        return header + body

    def assert_pofile_equal(self, pofile_path, expected_content):
        with open(pofile_path) as f:
            self.assertMultiLineEqual(f.read(), expected_content)

    def test_save_basic(self):
        """
        Test saving changes to an entity with a single translation.
        """
        test_input = self.generate_pofile(dedent("""
            #. Comment
            #: file.py:1
            msgid "Source String"
            msgstr "Translated String"
        """))
        path, resource = self.parse_string(test_input)

        translation = resource.translations[0]
        translation.strings[None] = 'New Translated String'
        translation.fuzzy = True
        resource.save(self.locale)

        self.assert_pofile_equal(path, self.generate_pofile(dedent("""
            #. Comment
            #: file.py:1
            #, fuzzy
            msgid "Source String"
            msgstr "New Translated String"
        """)))

    def test_save_plural(self):
        test_input = self.generate_pofile(dedent("""
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "Translated Plural %(count)s string"
            msgstr[1] "Translated Plural %(count)s strings"
        """))
        path, resource = self.parse_string(test_input)

        translation = resource.translations[0]
        translation.strings[0] = 'New Plural'
        translation.strings[1] = 'New Plurals'
        resource.save(self.locale)

        self.assert_pofile_equal(path, self.generate_pofile(dedent("""
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "New Plural"
            msgstr[1] "New Plurals"
        """)))

    def test_save_plural_remove(self):
        """Any missing plurals should be removed from the pofile."""
        test_input = self.generate_pofile(dedent("""
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "Translated Plural %(count)s string"
            msgstr[1] "Translated Plural %(count)s strings"
        """))
        path, resource = self.parse_string(test_input)

        translation = resource.translations[0]
        translation.strings[0] = 'New Plural'
        del translation.strings[1]
        resource.save(self.locale)

        self.assert_pofile_equal(path, self.generate_pofile(dedent("""
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "New Plural"
        """)))

    def test_save_remove_fuzzy(self):
        test_input = self.generate_pofile(dedent("""
            #, fuzzy
            msgid "Source String"
            msgstr "Translated String"
        """))
        path, resource = self.parse_string(test_input)

        resource.translations[0].fuzzy = False
        resource.save(self.locale)

        self.assert_pofile_equal(path, self.generate_pofile(dedent("""
            msgid "Source String"
            msgstr "Translated String"
        """)))

    def test_save_metadata(self):
        """Ensure pofile metadata is updated correctly."""
        test_input = self.generate_pofile('',
            language='different_code',
            generator='Not Pontoon',
            plural_forms='nplurals=1; plural=0;'
        )
        path, resource = self.parse_string(test_input)

        resource.save(self.locale)
        self.assert_pofile_equal(path, self.generate_pofile('',
            language='test_locale',
            generator='Pontoon',
            plural_forms='nplurals=2; plural=(n != 1);'
        ))

    def test_save_extra_metadata(self):
        """
        If last_updated or last_translator is set on the latest
        translation, update the metadata for those fields.
        """
        test_input = self.generate_pofile(
            dedent("""
                msgid "Latest"
                msgstr "Latest"

                msgid "Older"
                msgstr "Older"
            """),
            revision_date='2012-01-01 00:00+0000',
            last_translator='last <last@example.com>'
        )
        path, resource = self.parse_string(test_input)

        latest_translation, older_translation = resource.translations
        latest_translation.last_updated = datetime(2015, 1, 1, 0, 0, 0)
        latest_translation.last_translator = UserFactory(
            first_name='New',
            email='new@example.com'
        )
        older_translation.last_updated = datetime(1970, 1, 1, 0, 0, 0)
        older_translation.last_translator = UserFactory(
            first_name='Old',
            email='old@example.com'
        )
        resource.save(self.locale)

        self.assert_pofile_equal(path, self.generate_pofile(
            dedent("""
                msgid "Latest"
                msgstr "Latest"

                msgid "Older"
                msgstr "Older"
            """),
            revision_date='2015-01-01 00:00',
            last_translator='New <new@example.com>'
        ))
