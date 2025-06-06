from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from pontoon.sync.formats import parse_translations


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

        with TemporaryDirectory() as dir:
            path = join(dir, "messages.ftl")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2 = parse_translations(path)

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
