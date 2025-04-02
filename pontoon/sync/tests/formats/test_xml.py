from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from pontoon.sync.formats import parse_translations


class AndroidXMLTests(TestCase):
    def test_android(self):
        src = dedent("""
            <?xml version="1.0" encoding="utf-8"?>
            <resources>
                <!-- Sample comment -->
                <string name="Source String">Translated String</string>

                <!-- First comment -->
                <!-- Second comment -->
                <string name="Multiple Comments">Translated Multiple Comments</string>

                <string name="No Comments or Sources">Translated No Comments or Sources</string>
                <string name="Empty Translation"></string>
            </resources>
            """).strip()

        with TemporaryDirectory() as dir:
            path = join(dir, "strings.xml")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2, t3 = parse_translations(path)

            # basic
            assert t0.comments == ["Sample comment"]
            assert t0.key == "Source String"
            assert t0.context == "Source String"
            assert t0.strings == {None: "Translated String"}
            assert t0.order == 0

            # multiple comments
            assert t1.comments == ["First comment", "", "Second comment"]
            assert t1.key == "Multiple Comments"
            assert t1.strings == {None: "Translated Multiple Comments"}
            assert t1.order == 1

            # no comments or sources
            assert t2.comments == []
            assert t2.key == "No Comments or Sources"
            assert t2.strings == {None: "Translated No Comments or Sources"}
            assert t2.order == 2

            # empty translation
            assert t3.comments == []
            assert t3.key == "Empty Translation"
            assert t3.strings == {None: ""}
            assert t3.order == 3

    def test_android_quotes(self):
        src = dedent("""
            <?xml version="1.0" encoding="utf-8"?>
            <resources>
                <string name="String">\'</string>
            </resources>
            """).strip()

        with TemporaryDirectory() as dir:
            path = join(dir, "strings.xml")
            with open(path, "x") as file:
                file.write(src)
            (t0,) = parse_translations(path)
            assert t0.strings == {None: "'"}
