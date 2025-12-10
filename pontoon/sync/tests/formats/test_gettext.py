from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_entity, as_repo_translations


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

        res = parse_resource(Format.gettext, src, gettext_plurals=["one", "other"])
        e0, e1, e2, e3, e4, e5, e6, e7 = (
            as_entity(Format.gettext, (), entry, date_created=datetime.now())
            for entry in res.all_entries()
        )
        t0, t1, t2, t3, t4, t6, t7 = as_repo_translations(res)

        # basic
        assert e0.comment == "Sample comment"
        assert e0.key == ["Source String"]
        assert e0.meta == [["reference", "file.py:1"]]
        assert e0.string == "Source String"
        assert e0.value == ["Source String"]

        assert t0.key == ("Source String",)
        assert t0.string == "Translated String"
        assert not t0.fuzzy

        # multiple comments
        assert e1.comment == "First comment\nSecond comment"
        assert e1.key == ["Multiple Comments"]
        assert e1.string == "Multiple Comments"
        assert e1.value == ["Multiple Comments"]

        assert t1.key == ("Multiple Comments",)
        assert t1.string == "Translated Multiple Comments"
        assert not t1.fuzzy

        # multiple sources
        assert e2.comment == ""
        assert e2.meta == [["reference", "file.py:2"], ["reference", "file.py:3"]]
        assert e2.key == ["Multiple Sources"]
        assert e2.string == "Multiple Sources"
        assert e2.value == ["Multiple Sources"]

        assert t2.key == ("Multiple Sources",)
        assert t2.string == "Translated Multiple Sources"
        assert not t2.fuzzy

        # fuzzy
        assert e3.comment == ""
        assert e3.key == ["Fuzzy"]
        assert e3.string == "Fuzzy"
        assert e3.value == ["Fuzzy"]

        assert t3.key == ("Fuzzy",)
        assert t3.string == "Translated Fuzzy"
        assert t3.fuzzy

        # no comments or sources
        assert e4.comment == ""
        assert e4.key == ["No Comments or Sources"]
        assert e4.string == "No Comments or Sources"
        assert e4.value == ["No Comments or Sources"]

        assert t4.key == ("No Comments or Sources",)
        assert t4.string == "Translated No Comments or Sources"
        assert not t4.fuzzy

        # missing translation
        assert e5.comment == ""
        assert e5.key == ["Missing Translation"]
        assert e5.string == "Missing Translation"
        assert e5.value == ["Missing Translation"]

        # plural translation
        assert e6.comment == ""
        assert e6.key == ["Plural %(count)s string"]
        assert (
            e6.string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{Plural %(count)s string}}
                * {{Plural %(count)s strings}}
                """).strip()
        )
        assert e6.value == {
            "decl": {"n": {"$": "n", "fn": "number"}},
            "sel": ["n"],
            "alt": [
                {"keys": ["one"], "pat": ["Plural %(count)s string"]},
                {"keys": [{"*": "other"}], "pat": ["Plural %(count)s strings"]},
            ],
        }
        assert t6.key == ("Plural %(count)s string",)
        assert (
            t6.string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{Translated Plural %(count)s string}}
                * {{Translated Plural %(count)s strings}}
                """).strip()
        )
        assert not t6.fuzzy

        # missing plural translation
        assert e7.comment == ""
        assert e7.key == ["Plural %(count)s string with missing translation"]
        assert (
            e7.string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{Plural %(count)s string with missing translation}}
                * {{Plural %(count)s strings with missing translations}}
                """).strip()
        )
        assert e7.value == {
            "decl": {"n": {"$": "n", "fn": "number"}},
            "sel": ["n"],
            "alt": [
                {
                    "keys": ["one"],
                    "pat": ["Plural %(count)s string with missing translation"],
                },
                {
                    "keys": [{"*": "other"}],
                    "pat": ["Plural %(count)s strings with missing translations"],
                },
            ],
        }
        assert t7.key == ("Plural %(count)s string with missing translation",)
        assert (
            t7.string
            == dedent("""
                .input {$n :number}
                .match $n
                one {{}}
                * {{Translated Plural %(count)s strings with missing translations}}
                """).strip()
        )
        assert not t7.fuzzy

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

        res = parse_resource(Format.gettext, src)
        e0, e1, e2 = (
            as_entity(Format.gettext, (), entry, date_created=datetime.now())
            for entry in res.all_entries()
        )
        assert list(as_repo_translations(res)) == []

        assert e0.key == ["Source", "Main context"]
        assert e0.string == "Source"
        assert e0.value == ["Source"]

        assert e1.key == ["Source", "Other context"]
        assert e1.string == dedent("""\
            .input {$n :number}
            .match $n
            one {{Source}}
            * {{Source Plural}}""")
        assert e1.value == {
            "decl": {"n": {"$": "n", "fn": "number"}},
            "sel": ["n"],
            "alt": [
                {"keys": ["one"], "pat": ["Source"]},
                {"keys": [{"*": "other"}], "pat": ["Source Plural"]},
            ],
        }
        assert e2.key == ["Source"]
        assert e2.string == "Source"
        assert e2.value == ["Source"]
