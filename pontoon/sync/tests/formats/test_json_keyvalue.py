from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from pontoon.sync.formats import parse_translations


class JsonKeyValueTests(TestCase):
    def test_plain_json(self):
        src = dedent("""
            {
              "No Comments or Sources": "Translated No Comments or Sources",
              "Nested": {
                "key": "value"
              }
            }
            """)

        with TemporaryDirectory() as dir:
            path = join(dir, "file.json")
            with open(path, "x") as file:
                file.write(src)
            t0, t1 = parse_translations(path)

        assert t0.key == '["No Comments or Sources"]'
        assert t0.context == "No Comments or Sources"
        assert t0.strings == {None: "Translated No Comments or Sources"}
        assert t0.comments == []
        assert t0.source == []
        assert t0.order == 0

        assert t1.key == '["Nested", "key"]'
        assert t1.context == "Nested.key"
        assert t1.strings == {None: "value"}
        assert t1.comments == []
        assert t1.source == []
        assert t1.order == 1

    def test_key_conflict(self):
        src = dedent("""
            {
                "Source": { "String": "foo" },
                "Source.String": "bar",
                "[\\"Source\\", \\"String\\"]": "eek"
            }
            """)

        with TemporaryDirectory() as dir:
            path = join(dir, "file.json")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2 = parse_translations(path)

        assert t0.key == '["Source", "String"]'
        assert t0.context == "Source.String"
        assert t0.strings == {None: "foo"}

        assert t1.key == '["Source.String"]'
        assert t1.context == "Source.String"
        assert t1.strings == {None: "bar"}

        assert t2.key == '["[\\"Source\\", \\"String\\"]"]'
        assert t2.context == '["Source", "String"]'
        assert t2.strings == {None: "eek"}
