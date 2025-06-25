from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations


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
        t0, t1, t2, t3 = as_vcs_translations(res)

        # basic
        assert t0.comments == ["Sample comment"]
        assert t0.key == "SourceString"
        assert t0.context == "SourceString"
        assert t0.string == "Translated String"
        assert t0.order == 0

        # multiple comments
        assert t1.comments == ["First comment", "Second comment"]
        assert t1.key == "MultipleComments"
        assert t1.string == "Translated Multiple Comments"
        assert t1.order == 1

        # no comments or sources
        assert t2.comments == []
        assert t2.key == "NoCommentsorSources"
        assert t2.string == "Translated No Comments or Sources"
        assert t2.order == 2

        # empty translation
        assert t3.comments == []
        assert t3.key == "EmptyTranslation"
        assert t3.string == ""
        assert t3.order == 3


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
        t0, t1, t2, t3 = as_vcs_translations(res)

        # basic
        assert t0.comments == ["Sample comment"]
        assert t0.key == "SourceString"
        assert t0.context == "SourceString"
        assert t0.string == "Translated String"
        assert t0.order == 0

        # multiple comments
        assert t1.comments == ["First comment", "Second comment"]
        assert t1.key == "MultipleComments"
        assert t1.string == "Translated Multiple Comments"
        assert t1.order == 1

        # no comments or sources
        assert t2.comments == []
        assert t2.key == "NoCommentsorSources"
        assert t2.string == "Translated No Comments or Sources"
        assert t2.order == 2

        # empty translation
        assert t3.comments == []
        assert t3.key == "EmptyTranslation"
        assert t3.string == ""
        assert t3.order == 3
