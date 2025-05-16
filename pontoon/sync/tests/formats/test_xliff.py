from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from pontoon.sync.formats import ParseError, parse_translations


class XLIFFTests(TestCase):
    def test_xliff(self):
        src = dedent("""
            <xliff version="1.2">
                <file original="filename" source-language="en" datatype="plaintext" target-language="en">
                    <body>
                        <trans-unit id="Source String Key">
                            <source>Source &lt;b&gt;String&lt;/b&gt;</source>
                            <target>Translated &lt;b&gt;String&lt;/b&gt;</target>
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
            """)

        with TemporaryDirectory() as dir:
            path = join(dir, "file.xliff")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2, t3 = parse_translations(path)

            # basic
            assert t0.comments == ["Sample comment"]
            assert t0.key == "filename\x04Source String Key"
            assert t0.context == "Source String Key"
            assert t0.strings == {None: "Translated <b>String</b>"}
            assert t0.source_string == "Source <b>String</b>"
            assert t0.source_string_plural == ""
            assert t0.order == 0

            # multiple comments
            assert t1.comments == ["First comment", "Second comment"]
            assert t1.key == "filename\x04Multiple Comments Key"
            assert t1.strings == {None: "Translated Multiple Comments"}
            assert t1.source_string == "Multiple Comments"
            assert t1.source_string_plural == ""
            assert t1.order == 1

            # no comments or sources
            assert t2.comments == []
            assert t2.key == "filename\x04No Comments or Sources Key"
            assert t2.strings == {None: "Translated No Comments or Sources"}
            assert t2.source_string == "No Comments or Sources"
            assert t2.source_string_plural == ""
            assert t2.order == 2

            # missing translation
            assert t3.comments == []
            assert t3.key == "filename\x04Missing Translation Key"
            assert t3.strings == {}
            assert t3.source_string == "Missing Translation"
            assert t3.source_string_plural == ""
            assert t3.order == 3

    def test_invalid_xliff(self):
        src = dedent("""
            <xliff version="1.2">
                <file original="filename" source-language="en" datatype="plaintext" target-language="en">
                    <body>
                        <trans-unit id="Source String Key"
                            <source>Source String</source>
                            <target>Translated String</target>
                        </trans-unit>
                    </body>
                </file>
            </xliff>
            """)

        with TemporaryDirectory() as dir:
            path = join(dir, "file.xlf")
            with open(path, "x") as file:
                file.write(src)
            with self.assertRaises(ParseError):
                parse_translations(path)
