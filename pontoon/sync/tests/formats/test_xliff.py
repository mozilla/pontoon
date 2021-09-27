from difflib import Differ
from textwrap import dedent

import pytest

from pontoon.base.tests import TestCase
from pontoon.sync import KEY_SEPARATOR
from pontoon.sync.exceptions import ParseError
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
    <file original="filename" source-language="en" datatype="plaintext" {attr}>
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
        return "filename" + KEY_SEPARATOR + super().key(source_string)

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

    def test_parse_invalid_translation(self):
        """
        If a resource has an invalid translation, raise a ParseError.
        """
        with pytest.raises(ParseError):
            self.parse_string(
                dedent(
                    """
                <trans-unit id="Source String Key"
                    <source>Source String</source>
                    <target>Translated String</target>
                </trans-unit>
            """
                )
            )

    def generate_xliff(self, body, attr=""):
        return XLIFF_TEMPLATE.format(body=body, attr=attr)

    def test_save_basic(self):
        """
        Test saving changes to an entity with a single translation.

        Make sure the target-language attribute is set when not present.
        """
        attr = f'target-language="{self.locale.code}"'

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
            <trans-unit id="Source String Key" xml:space="preserve">
                <source>Source String</source>
                <target>New Translated String</target>
                <note>Comment</note>
            </trans-unit>
        """
            ),
            attr=attr,
        )

        super().run_save_basic(input_string, expected_string)

    def test_save_preserve_target_language(self):
        """
        Test that the existing target-language attribute is preserved.
        """
        attr = 'target-language="locale-code"'

        input_string = self.generate_xliff(
            dedent(
                """
            <trans-unit id="Source String Key">
                <source>Source String</source>
                <target>Translated String</target>
                <note>Comment</note>
            </trans-unit>
        """
            ),
            attr=attr,
        )

        expected_string = self.generate_xliff(
            dedent(
                """
            <trans-unit id="Source String Key" xml:space="preserve">
                <source>Source String</source>
                <target>New Translated String</target>
                <note>Comment</note>
            </trans-unit>
        """
            ),
            attr=attr,
        )

        super().run_save_basic(input_string, expected_string)

    def test_save_remove(self):
        attr = f'target-language="{self.locale.code}"'

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
            attr=attr,
        )

        super().run_save_remove(input_string, expected_string)
