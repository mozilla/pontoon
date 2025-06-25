from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations


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

        res = parse_resource(Format.plain_json, src)
        t0, t1 = as_vcs_translations(res)

        assert t0.key == '["No Comments or Sources"]'
        assert t0.context == "No Comments or Sources"
        assert t0.string == "Translated No Comments or Sources"
        assert t0.comments == []
        assert t0.source == []
        assert t0.order == 0

        assert t1.key == '["Nested", "key"]'
        assert t1.context == "Nested.key"
        assert t1.string == "value"
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

        res = parse_resource(Format.plain_json, src)
        t0, t1, t2 = as_vcs_translations(res)

        assert t0.key == '["Source", "String"]'
        assert t0.context == "Source.String"
        assert t0.string == "foo"

        assert t1.key == '["Source.String"]'
        assert t1.context == "Source.String"
        assert t1.string == "bar"

        assert t2.key == '["[\\"Source\\", \\"String\\"]"]'
        assert t2.context == '["Source", "String"]'
        assert t2.string == "eek"
