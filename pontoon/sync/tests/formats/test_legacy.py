from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from pontoon.sync.formats import parse_translations


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

        with TemporaryDirectory() as dir:
            path = join(dir, "file.dtd")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2, t3 = parse_translations(path)

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

        with TemporaryDirectory() as dir:
            path = join(dir, "file.ini")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2, t3 = parse_translations(path)

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


class IncTests(TestCase):
    def test_inc(self):
        src = dedent("""
            # Sample comment
            #define SourceString Translated String

            # First comment
            # Second comment
            #define MultipleComments Translated Multiple Comments

            #define NoCommentsorSources Translated No Comments or Sources

            #define EmptyTranslation
            """)

        with TemporaryDirectory() as dir:
            path = join(dir, "file.inc")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2, t3 = parse_translations(path)

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
