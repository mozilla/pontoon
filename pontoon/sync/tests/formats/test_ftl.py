from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.model import Entry
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations
from pontoon.sync.formats.ftl import ftl_as_entity


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
        e0, e1, e2 = (
            ftl_as_entity(res, section, entry, datetime.now())
            for section in res.sections
            for entry in section.entries
            if isinstance(entry, Entry)
        )
        t0, t1, t2 = as_vcs_translations(res)

        # basic
        assert e0.comment == "Sample comment"
        assert e0.key == "SourceString"
        assert e0.context == "SourceString"
        assert e0.string == "SourceString = Translated String\n"
        assert t0.key == "SourceString"
        assert t0.string == "SourceString = Translated String\n"

        # multiple comments
        assert e1.comment == "First comment\nSecond comment"
        assert e1.key == "MultipleComments"
        assert e1.string == "MultipleComments = Translated Multiple Comments\n"
        assert t1.key == "MultipleComments"
        assert t1.string == "MultipleComments = Translated Multiple Comments\n"

        # no comments or sources
        assert e2.comment == ""
        assert e2.key == "NoCommentsOrSources"
        assert e2.string == "NoCommentsOrSources = Translated No Comments or Sources\n"
        assert t2.key == "NoCommentsOrSources"
        assert t2.string == "NoCommentsOrSources = Translated No Comments or Sources\n"
