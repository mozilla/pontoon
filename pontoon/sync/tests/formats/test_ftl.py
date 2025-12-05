from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_entity, as_repo_translations


class FTLTests(TestCase):
    def test_fluent(self):
        src = dedent("""
            # Sample comment
            SourceString = Translated String

            # First comment
            # Second comment
            MultipleComments = Translated Multiple Comments

            NoCommentsOrSources = Translated No Comments or Sources

            plural =
                { $n ->
                    [one] { $n } thing
                   *[other] { $n } things
                }
            select =
                { PLATFORM() ->
                    [mac] Mac
                   *[other] PC
                }
            msg-key =
                .attr = Attribute
            -term-key = Term
                .attr = Attribute
            """)

        res = parse_resource(Format.fluent, src)
        e0, e1, e2, e3, e4, e5, e6 = (
            as_entity(Format.fluent, (), entry, date_created=datetime.now())
            for entry in res.all_entries()
        )
        t0, t1, t2, t3, t4, t5, t6 = as_repo_translations(res)

        # basic
        assert e0.comment == "Sample comment"
        assert e0.key == ["SourceString"]
        assert e0.string == "SourceString = Translated String\n"
        assert e0.value == ["Translated String"]
        assert t0.key == ("SourceString",)
        assert t0.string == "SourceString = Translated String\n"

        # multiple comments
        assert e1.comment == "First comment\nSecond comment"
        assert e1.key == ["MultipleComments"]
        assert e1.string == "MultipleComments = Translated Multiple Comments\n"
        assert e1.value == ["Translated Multiple Comments"]
        assert t1.key == ("MultipleComments",)
        assert t1.string == "MultipleComments = Translated Multiple Comments\n"

        # no comments or sources
        assert e2.comment == ""
        assert e2.key == ["NoCommentsOrSources"]
        assert e2.string == "NoCommentsOrSources = Translated No Comments or Sources\n"
        assert e2.value == ["Translated No Comments or Sources"]
        assert t2.key == ("NoCommentsOrSources",)
        assert t2.string == "NoCommentsOrSources = Translated No Comments or Sources\n"

        # plural
        assert e3.string == dedent("""\
            plural =
                { $n ->
                    [one] { $n } thing
                   *[other] { $n } things
                }
            """)
        assert e3.value == {
            "decl": {"n_1": {"$": "n", "fn": "number"}},
            "sel": ["n_1"],
            "alt": [
                {"keys": ["one"], "pat": [{"$": "n"}, " thing"]},
                {"keys": [{"*": "other"}], "pat": [{"$": "n"}, " things"]},
            ],
        }
        assert t3.string == dedent("""\
            plural =
                { $n ->
                    [one] { $n } thing
                   *[other] { $n } things
                }
            """)

        # select
        assert e4.string == dedent("""\
            select =
                { PLATFORM() ->
                    [mac] Mac
                   *[other] PC
                }
            """)
        assert e4.value == {
            "decl": {"_1": {"fn": "platform"}},
            "sel": ["_1"],
            "alt": [
                {"keys": ["mac"], "pat": ["Mac"]},
                {"keys": [{"*": "other"}], "pat": ["PC"]},
            ],
        }
        assert t4.string == dedent("""\
            select =
                { PLATFORM() ->
                    [mac] Mac
                   *[other] PC
                }
            """)

        # message with attribute
        assert e5.string == dedent("""\
            msg-key =
                .attr = Attribute
            """)
        assert e5.value == []
        assert e5.properties == {"attr": ["Attribute"]}
        assert t5.string == dedent("""\
            msg-key =
                .attr = Attribute
            """)

        # term with attribute
        assert e6.string == dedent("""\
            -term-key = Term
                .attr = Attribute
            """)
        assert e6.value == ["Term"]
        assert e6.properties == {"attr": ["Attribute"]}
        assert t6.string == dedent("""\
            -term-key = Term
                .attr = Attribute
            """)
