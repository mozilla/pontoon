from difflib import Differ
from textwrap import dedent

from pontoon.base.tests import TestCase
from pontoon.sync import KEY_SEPARATOR
from pontoon.sync.formats import xliff
from pontoon.sync.tests.formats import FormatTestsMixin


BASE_XLIFF_FILE = """
<xliff>
    <file original="filename" source-language="en" datatype="plaintext" target-language="en">
        <body>
            <trans-unit id="Source String Key">
                <source>Source String</source>
                <target>Translated String</target>
                <note>Sample comment</note>
            </trans-unit>
            <trans-unit id="Multiple Comments Key">
                <source>Multiple Comments</source>
                <target>Translated Multiple Comments</target>
                <note>First comment</note>
                <note>Second comment</note>
            </trans-unit>
            <trans-unit id="No Comments or Sources Key">
                <source>No Comments or Sources</source>
                <target>Translated No Comments or Sources</target>
            </trans-unit>
            <trans-unit id="Missing Translation Key">
                <source>Missing Translation</source>
            </trans-unit>
        </body>
    </file>
</xliff>
"""


XLIFF_TEMPLATE = """
<xliff>
    <file original="filename" source-language="en" datatype="plaintext"
          target-language="{locale_code}">
        <body>
            {body}
        </body>
    </file>
</xliff>
"""


class XLIFFTests(FormatTestsMixin, TestCase):
    parse = staticmethod(xliff.parse)
    supports_keys = True
    supports_source = False
    supports_source_string = True

    def key(self, source_string):
        """XLIFF keys are prefixed with the file name."""
        return u"filename" + KEY_SEPARATOR + super(XLIFFTests, self).key(source_string)

    def assert_file_content(self, file_path, expected_content):
        """
        Compare XML file contents as XML rather than direct strings.
        """
        with open(file_path) as f:
            file_content = f.read()

            # Generate a diff for the error message.
            result = Differ().compare(
                file_content.splitlines(1), expected_content.splitlines(1)
            )
            msg = "XML strings are not equal:\n" + "".join(result)

            self.assertXMLEqual(file_content, expected_content, msg)

    def test_parse_basic(self):
        self.run_parse_basic(BASE_XLIFF_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_XLIFF_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_XLIFF_FILE, 2)

    def test_parse_missing_translation(self):
        self.run_parse_missing_translation(BASE_XLIFF_FILE, 3)

    def generate_xliff(self, body, locale_code="en"):
        return XLIFF_TEMPLATE.format(body=body, locale_code=locale_code)

    def test_save_basic(self):
        """
        Test saving changes to an entity with a single translation.

        Also happens to test if the locale code is saved correctly.
        """
        input_string = self.generate_xliff(
            dedent(
                """
            <trans-unit id="Source String Key">
                <source>Source String</source>
                <target>Translated String</target>
                <note>Comment</note>
            </trans-unit>
        """
            )
        )

        expected_string = self.generate_xliff(
            dedent(
                """
            <trans-unit id="Source String Key">
                <source>Source String</source>
                <target>New Translated String</target>
                <note>Comment</note>
            </trans-unit>
        """
            ),
            locale_code=self.locale.code,
        )

        super(XLIFFTests, self).run_save_basic(input_string, expected_string)

    def test_save_remove(self):
        input_string = self.generate_xliff(
            dedent(
                """
            <trans-unit id="Source String Key">
                <source>Source String</source>
                <target>Translated String</target>
                <note>Comment</note>
            </trans-unit>
        """
            )
        )

        expected_string = self.generate_xliff(
            dedent(
                """
            <trans-unit id="Source String Key">
                <source>Source String</source>
                <note>Comment</note>
            </trans-unit>
        """
            ),
            locale_code=self.locale.code,
        )

        super(XLIFFTests, self).run_save_remove(input_string, expected_string)
