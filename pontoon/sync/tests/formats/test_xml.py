from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations


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
        t0, t1, t2, t3 = as_vcs_translations(res)

        # basic
        assert t0.comments == ["Sample comment"]
        assert t0.key == "Source String"
        assert t0.context == "Source String"
        assert t0.string == "Translated <b>String</b>"
        assert t0.order == 0

        # multiple comments
        assert t1.comments == ["First comment", "", "Second comment"]
        assert t1.key == "Multiple Comments"
        assert t1.string == "Translated Multiple Comments"
        assert t1.order == 1

        # no comments or sources
        assert t2.comments == []
        assert t2.key == "No Comments or Sources"
        assert t2.string == "Translated No Comments or Sources"
        assert t2.order == 2

        # empty translation
        assert t3.comments == []
        assert t3.key == "Empty Translation"
        assert t3.string == ""
        assert t3.order == 3

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
