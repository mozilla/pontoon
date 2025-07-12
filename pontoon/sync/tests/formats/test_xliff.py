from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.model import Entry
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations
from pontoon.sync.formats.xliff import xliff_as_entity


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

        res = parse_resource(Format.xliff, src)
        e0, e1, e2, e3 = (
            xliff_as_entity(section.id, entry, datetime.now())
            for section in res.sections
            for entry in section.entries
            if isinstance(entry, Entry)
        )
        t0, t1, t2, t3 = as_vcs_translations(res)

        # basic
        assert e0.comment == "Sample comment"
        assert e0.new_key == ["filename", "Source String Key"]
        assert e0.string == "Source <b>String</b>"

        assert t0.key == ("filename", "Source String Key")
        assert t0.string == "Translated <b>String</b>"

        # multiple comments
        assert e1.comment == "First comment\nSecond comment"
        assert e1.new_key == ["filename", "Multiple Comments Key"]
        assert e1.string == "Multiple Comments"

        assert t1.key == ("filename", "Multiple Comments Key")
        assert t1.string == "Translated Multiple Comments"

        # no comments or sources
        assert e2.comment == ""
        assert e2.new_key == ["filename", "No Comments or Sources Key"]
        assert e2.string == "No Comments or Sources"

        assert t2.key == ("filename", "No Comments or Sources Key")
        assert t2.string == "Translated No Comments or Sources"

        # missing translation
        assert e3.comment == ""
        assert e3.new_key == ["filename", "Missing Translation Key"]
        assert e3.string == "Missing Translation"

        assert t3.key == ("filename", "Missing Translation Key")
        assert t3.string is None
