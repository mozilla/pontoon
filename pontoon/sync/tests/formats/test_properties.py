from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_entity, as_vcs_translations


class PropertiesTests(TestCase):
    def test_properties(self):
        src = dedent("""
            # Sample comment
            SourceString=Translated String\\u0020

            # First comment
            # Second comment
            MultipleComments=Translated Multiple Comments

            NoCommentsorSources=Translated No Comments or Sources

            EmptyTranslation=
            """)

        res = parse_resource(Format.properties, src)
        e0, e1, e2, e3 = (
            as_entity(Format.properties, (), entry, date_created=datetime.now())
            for entry in res.all_entries()
        )
        t0, t1, t2, t3 = as_vcs_translations(res)

        # basic
        assert e0.comment == "Sample comment"
        assert e0.key == ["SourceString"]
        assert e0.string == "Translated String "

        assert t0.key == ("SourceString",)
        assert t0.string == "Translated String "

        # multiple comments
        assert e1.comment == "First comment\nSecond comment"
        assert e1.key == ["MultipleComments"]
        assert e1.string == "Translated Multiple Comments"

        assert t1.key == ("MultipleComments",)
        assert t1.string == "Translated Multiple Comments"

        # no comments or sources
        assert e2.comment == ""
        assert e2.key == ["NoCommentsorSources"]
        assert e2.string == "Translated No Comments or Sources"

        assert t2.key == ("NoCommentsorSources",)
        assert t2.string == "Translated No Comments or Sources"

        # empty translation
        assert e3.comment == ""
        assert e3.key == ["EmptyTranslation"]
        assert e3.string == ""

        assert t3.key == ("EmptyTranslation",)
        assert t3.string == ""
