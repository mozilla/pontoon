from textwrap import dedent

from pontoon.base.tests import assert_attributes_equal, TestCase, UserFactory
from pontoon.base.utils import aware_datetime
from pontoon.sync import KEY_SEPARATOR
from pontoon.sync.formats import po
from pontoon.sync.tests.formats import FormatTestsMixin


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


class POTests(FormatTestsMixin, TestCase):
    parse = staticmethod(po.parse)
    supports_keys = False
    supports_source = True
    supports_source_string = True

    def test_parse_basic(self):
        self.run_parse_basic(BASE_POFILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_POFILE, 1)

    def test_parse_multiple_sources(self):
        self.run_parse_multiple_sources(BASE_POFILE, 2)

    def test_parse_fuzzy(self):
        self.run_parse_fuzzy(BASE_POFILE, 3)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_POFILE, 4)

    def test_parse_missing_translation(self):
        self.run_parse_missing_translation(BASE_POFILE, 5)

    def test_parse_plural_translation(self):
        self.run_parse_plural_translation(BASE_POFILE, 6)

    def test_parse_plural_translation_missing(self):
        self.run_parse_plural_translation_missing(BASE_POFILE, 7)

    def test_parse_context(self):
        """
        Test that entities with different context are parsed as separate.
        """
        test_input = self.generate_pofile(
            dedent(
                """
                msgctxt "Main context"
                msgid "Source"
                msgstr ""

                msgctxt "Other context"
                msgid "Source"
                msgstr ""

                msgid "Source"
                msgstr ""
            """
            )
        )
        path, resource = self.parse_string(test_input)

        assert_attributes_equal(
            resource.translations[0],
            source_string="Source",
            key=self.key("Main context" + KEY_SEPARATOR + "Source"),
        )

        assert_attributes_equal(
            resource.translations[1],
            source_string="Source",
            key=self.key("Other context" + KEY_SEPARATOR + "Source"),
        )

        assert_attributes_equal(
            resource.translations[2], source_string="Source", key=self.key("Source"),
        )

    def generate_pofile(
        self,
        body,
        revision_date="2015-08-04 12:30+0000",
        last_translator="example <example@example.com>",
        language="test_locale",
        plural_forms="nplurals=2; plural=(n != 1);",
        generator="Pontoon",
    ):
        header = HEADER_TEMPLATE.format(
            revision_date=revision_date,
            last_translator=last_translator,
            language=language,
            plural_forms=plural_forms,
            generator=generator,
        )
        return header + body

    def test_save_basic(self):
        """
        Test saving changes to an entity with a single translation.
        """
        input_string = self.generate_pofile(
            dedent(
                """
            #. Comment
            #: file.py:1
            msgid "Source String"
            msgstr "Translated String"
        """
            )
        )

        expected_string = self.generate_pofile(
            dedent(
                """
            #. Comment
            #: file.py:1
            #, fuzzy
            msgid "Source String"
            msgstr "New Translated String"
        """
            )
        )

        self.run_save_basic(input_string, expected_string)

    def test_save_remove(self):
        input_string = self.generate_pofile(
            dedent(
                """
            #. Comment
            #: file.py:1
            msgid "Source String"
            msgstr "Translated String"
        """
            )
        )

        expected_string = self.generate_pofile(
            dedent(
                """
            #. Comment
            #: file.py:1
            msgid "Source String"
            msgstr ""
        """
            )
        )

        self.run_save_remove(input_string, expected_string)

    def test_save_plural(self):
        input_string = self.generate_pofile(
            dedent(
                """
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "Translated Plural %(count)s string"
            msgstr[1] "Translated Plural %(count)s strings"
        """
            )
        )

        expected_string = self.generate_pofile(
            dedent(
                """
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "New Plural"
            msgstr[1] "New Plurals"
        """
            )
        )

        self.run_save_plural(input_string, expected_string)

    def test_save_plural_remove(self):
        """
        Any missing plurals should be set to an empty string in the
        pofile.
        """
        input_string = self.generate_pofile(
            dedent(
                """
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "Translated Plural %(count)s string"
            msgstr[1] "Translated Plural %(count)s strings"
        """
            )
        )

        expected_string = self.generate_pofile(
            dedent(
                """
            msgid "Plural %(count)s string"
            msgid_plural "Plural %(count)s strings"
            msgstr[0] "New Plural"
            msgstr[1] ""
        """
            )
        )

        self.run_save_plural_remove(input_string, expected_string)

    def test_save_remove_fuzzy(self):
        input_string = self.generate_pofile(
            dedent(
                """
            #, fuzzy
            msgid "Source String"
            msgstr "Translated String"
        """
            )
        )

        expected_string = self.generate_pofile(
            dedent(
                """
            msgid "Source String"
            msgstr "Translated String"
        """
            )
        )

        self.run_save_remove_fuzzy(input_string, expected_string)

    def test_save_preserve_fuzzy(self):
        """
        If the fuzzy status of an entity doesn't change, make sure to
        not remove it.
        """
        input_string = self.generate_pofile(
            dedent(
                """
            #, fuzzy
            msgid "Source String"
            msgstr "Translated String"
        """
            )
        )

        # String should be unchanged.
        self.run_save_no_changes(input_string, input_string)

    def test_save_metadata(self):
        """Ensure pofile metadata is updated correctly."""
        test_input = self.generate_pofile(
            "",
            language="different_code",
            generator="Not Pontoon",
            plural_forms="nplurals=1; plural=0;",
        )
        path, resource = self.parse_string(test_input)

        resource.save(self.locale)
        self.assert_file_content(
            path,
            self.generate_pofile(
                "",
                language="test_locale",
                generator="Pontoon",
                plural_forms="nplurals=2; plural=(n != 1);",
            ),
        )

    def test_save_extra_metadata(self):
        """
        If last_updated or last_translator is set on the latest
        translation, update the metadata for those fields.
        """
        test_input = self.generate_pofile(
            dedent(
                """
                msgid "Latest"
                msgstr "Latest"

                msgid "Older"
                msgstr "Older"
            """
            ),
            revision_date="2012-01-01 00:00+0000",
            last_translator="last <last@example.com>",
        )
        path, resource = self.parse_string(test_input)

        latest_translation, older_translation = resource.translations
        latest_translation.last_updated = aware_datetime(2015, 1, 1, 0, 0, 0)
        latest_translation.last_translator = UserFactory(
            first_name="New", email="new@example.com"
        )
        older_translation.last_updated = aware_datetime(1970, 1, 1, 0, 0, 0)
        older_translation.last_translator = UserFactory(
            first_name="Old", email="old@example.com"
        )
        resource.save(self.locale)

        self.assert_file_content(
            path,
            self.generate_pofile(
                dedent(
                    """
                msgid "Latest"
                msgstr "Latest"

                msgid "Older"
                msgstr "Older"
            """
                ),
                revision_date="2015-01-01 00:00+0000",
                last_translator="New <new@example.com>",
            ),
        )
