from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.model import Entry
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_entity


class DTDTests(TestCase):
    def test_dtd(self):
        src = dedent("""
            <!-- Sample comment -->
            <!ENTITY SourceString "Translated String">

            <!-- First comment -->
            <!-- Second comment -->
            <!ENTITY MultipleComments "Translated Multiple Comments">

            <!ENTITY NoCommentsorSources "Translated No Comments or Sources">

            <!ENTITY EmptyTranslation "">
            """)

        res = parse_resource(Format.dtd, src)
        e0, e1, e2, e3 = (
            as_entity(Format.dtd, (), entry, date_created=datetime.now())
            for entry in res.all_entries()
        )

        # basic
        assert e0.comment == "Sample comment"
        assert e0.key == ["SourceString"]
        assert e0.string == "Translated String"

        # multiple comments
        assert e1.comment == "First comment\nSecond comment"
        assert e1.key == ["MultipleComments"]
        assert e1.string == "Translated Multiple Comments"

        # no comments or sources
        assert e2.comment == ""
        assert e2.key == ["NoCommentsorSources"]
        assert e2.string == "Translated No Comments or Sources"

        # empty translation
        assert e3.comment == ""
        assert e3.key == ["EmptyTranslation"]
        assert e3.string == ""


class IniTests(TestCase):
    def test_ini(self):
        src = dedent("""
            [Strings]
            # Sample comment
            SourceString=Translated String

            # First comment
            # Second comment
            MultipleComments=Translated Multiple Comments

            NoCommentsorSources=Translated No Comments or Sources

            EmptyTranslation=
            """)

        res = parse_resource(Format.ini, src)
        e0, e1, e2, e3 = (
            as_entity(Format.ini, section.id, entry, date_created=datetime.now())
            for section in res.sections
            for entry in section.entries
            if isinstance(entry, Entry)
        )

        # basic
        assert e0.comment == "Sample comment"
        assert e0.key == ["Strings", "SourceString"]
        assert e0.string == "Translated String"

        # multiple comments
        assert e1.comment == "First comment\nSecond comment"
        assert e1.key == ["Strings", "MultipleComments"]
        assert e1.string == "Translated Multiple Comments"

        # no comments or sources
        assert e2.comment == ""
        assert e2.key == ["Strings", "NoCommentsorSources"]
        assert e2.string == "Translated No Comments or Sources"

        # empty translation
        assert e3.comment == ""
        assert e3.key == ["Strings", "EmptyTranslation"]
        assert e3.string == ""
