from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from pontoon.sync.formats import parse_translations


class GettextTests(TestCase):
    def test_gettext(self):
        src = dedent("""
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

            msgid "Plural %(count)s string with missing translation"
            msgid_plural "Plural %(count)s strings with missing translations"
            msgstr[0] ""
            msgstr[1] "Translated Plural %(count)s strings with missing translations"
            """)

        with TemporaryDirectory() as dir:
            path = join(dir, "file.po")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2, t3, t4, t5, t6, t7 = parse_translations(
                path, gettext_plurals=["one", "other"]
            )

        # basic
        assert t0.comments == ["Sample comment"]
        assert t0.key == "Source String"
        assert t0.string == "Translated String"
        assert t0.source == [("file.py", "1")]
        assert t0.source_string == "Source String"
        assert not t0.fuzzy
        assert t0.order == 0

        # multiple comments
        assert t1.comments == ["First comment", "Second comment"]
        assert t1.source == []
        assert t1.key == "Multiple Comments"
        assert t1.string == "Translated Multiple Comments"
        assert t1.source_string == "Multiple Comments"
        assert not t1.fuzzy
        assert t1.order == 1

        # multiple sources
        assert t2.comments == []
        assert t2.source == [("file.py", "2"), ("file.py", "3")]
        assert t2.key == "Multiple Sources"
        assert t2.string == "Translated Multiple Sources"
        assert t2.source_string == "Multiple Sources"
        assert not t2.fuzzy
        assert t2.order == 2

        # fuzzy
        assert t3.comments == []
        assert t3.source == []
        assert t3.key == "Fuzzy"
        assert t3.string == "Translated Fuzzy"
        assert t3.source_string == "Fuzzy"
        assert t3.fuzzy
        assert t3.order == 3

        # no comments or sources
        assert t4.comments == []
        assert t4.source == []
        assert t4.key == "No Comments or Sources"
        assert t4.string == "Translated No Comments or Sources"
        assert t4.source_string == "No Comments or Sources"
        assert not t4.fuzzy
        assert t4.order == 4

        # missing translation
        assert t5.comments == []
        assert t5.source == []
        assert t5.key == "Missing Translation"
        assert t5.string is None
        assert t5.source_string == "Missing Translation"
        assert not t5.fuzzy
        assert t5.order == 5

        # plural translation
        assert t6.comments == []
        assert t6.source == []
        assert t6.key == "Plural %(count)s string"
        assert (
            t6.string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{Translated Plural %(count)s string}}
                * {{Translated Plural %(count)s strings}}
                """).strip()
        )
        assert (
            t6.source_string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{Plural %(count)s string}}
                * {{Plural %(count)s strings}}
                """).strip()
        )
        assert not t6.fuzzy
        assert t6.order == 6

        # missing plural translation
        assert t7.comments == []
        assert t7.source == []
        assert t7.key == "Plural %(count)s string with missing translation"
        assert (
            t7.string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{}}
                * {{Translated Plural %(count)s strings with missing translations}}
                """).strip()
        )
        assert (
            t7.source_string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{Plural %(count)s string with missing translation}}
                * {{Plural %(count)s strings with missing translations}}
                """).strip()
        )
        assert not t7.fuzzy
        assert t7.order == 7

    def test_context_and_empty_messages(self):
        src = dedent("""
            #
            msgid ""
            msgstr ""
            "Project-Id-Version: PACKAGE VERSION\\n"
            "Report-Msgid-Bugs-To: \\n"
            "POT-Creation-Date: 2015-08-04 12:30+0000\\n"
            "PO-Revision-Date: 2015-08-04 12:30+0000\\n"
            "Last-Translator: example <example@example.com>\\n"
            "Language-Team: LANGUAGE <LL@li.org>\\n"
            "Language: test_locale\\n"
            "MIME-Version: 1.0\\n"
            "Content-Type: text/plain; charset=UTF-8\\n"
            "Content-Transfer-Encoding: 8bit\\n"
            "Plural-Forms: nplurals=2; plural=(n != 1);\\n"
            "Generated-By: Babel 0.9.5\\n"
            "X-Generator: Pontoon\\n"

            msgctxt "Main context"
            msgid "Source"
            msgstr ""

            msgctxt "Other context"
            msgid "Source"
            msgid_plural "Source Plural"
            msgstr[0] ""
            msgstr[1] ""

            msgid "Source"
            msgstr ""
            """)

        with TemporaryDirectory() as dir:
            path = join(dir, "file.po")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2 = parse_translations(path)

        assert t0.source_string == "Source"
        assert t0.key == "Main context\x04Source"
        assert t0.string is None

        assert t1.source_string == dedent("""\
            .input {$n :number}
            .match $n
            one {{Source}}
            * {{Source Plural}}""")
        assert t1.key == "Other context\x04Source"
        assert t1.string is None

        assert t2.source_string == "Source"
        assert t2.key == "Source"
        assert t2.string is None
