from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations
from pontoon.sync.formats.xml import android_as_entity


class AndroidXMLTests(TestCase):
    def test_android(self):
        src = dedent("""
            <?xml version="1.0" encoding="utf-8"?>
            <resources>
                <!-- Sample comment -->
                <string name="Source String">Translated &lt;b&gt;String&lt;/b&gt;</string>

                <!-- First comment -->
                <!-- Second comment -->
                <string name="Multiple Comments">Translated Multiple Comments</string>

                <string name="No Comments or Sources">Translated No Comments or Sources</string>
                <string name="Empty Translation"></string>
            </resources>
            """).strip()

        res = parse_resource(Format.android, src)
        e0, e1, e2, e3 = (
            android_as_entity(entry, datetime.now()) for entry in res.all_entries()
        )
        t0, t1, t2, t3 = as_vcs_translations(res)

        # basic
        assert e0.comment == "Sample comment"
        assert e0.key == "Source String"
        assert e0.context == "Source String"
        assert e0.string == "Translated <b>String</b>"

        assert t0.key == "Source String"
        assert t0.string == "Translated <b>String</b>"

        # multiple comments
        assert e1.comment == "First comment\n\nSecond comment"
        assert e1.key == "Multiple Comments"
        assert e1.string == "Translated Multiple Comments"

        assert t1.key == "Multiple Comments"
        assert t1.string == "Translated Multiple Comments"

        # no comments or sources
        assert e2.comment == ""
        assert e2.key == "No Comments or Sources"
        assert e2.string == "Translated No Comments or Sources"

        assert t2.key == "No Comments or Sources"
        assert t2.string == "Translated No Comments or Sources"

        # empty translation
        assert e3.comment == ""
        assert e3.key == "Empty Translation"
        assert e3.string == ""

        assert t3.key == "Empty Translation"
        assert t3.string == ""

    def test_android_quotes(self):
        src = dedent("""
            <?xml version="1.0" encoding="utf-8"?>
            <resources>
                <string name="String">\'</string>
            </resources>
            """).strip()
        res = parse_resource(Format.android, src)
        (t0,) = as_vcs_translations(res)
        assert t0.string == "'"

    def test_android_escapes_and_trimming(self):
        src = dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <resources>
                <string name="key"> \\u0020\\u000a </string>
            </resources>
            """)
        res = parse_resource(Format.android, src)
        (t0,) = as_vcs_translations(res)
        assert t0.string == " \\n\n"
