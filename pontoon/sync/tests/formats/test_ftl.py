from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations


class FTLTests(TestCase):
    def test_fluent(self):
        src = dedent("""
            # Sample comment
            SourceString = Translated String

            # First comment
            # Second comment
            MultipleComments = Translated Multiple Comments

            NoCommentsOrSources = Translated No Comments or Sources
            """)

        res = parse_resource(Format.fluent, src)
        t0, t1, t2 = as_vcs_translations(res)

        # basic
        assert t0.comments == ["Sample comment"]
        assert t0.key == "SourceString"
        assert t0.context == "SourceString"
        assert t0.string == "SourceString = Translated String\n"
        assert t0.order == 0

        # multiple comments
        assert t1.comments == ["First comment\nSecond comment"]
        assert t1.key == "MultipleComments"
        assert t1.string == "MultipleComments = Translated Multiple Comments\n"
        assert t1.order == 1

        # no comments or sources
        assert t2.comments == []
        assert t2.key == "NoCommentsOrSources"
        assert t2.string == "NoCommentsOrSources = Translated No Comments or Sources\n"
        assert t2.order == 2
