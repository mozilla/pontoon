from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_vcs_translations
from pontoon.sync.formats.json_keyvalue import plain_json_as_entity


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
        e0, e1 = (
            plain_json_as_entity(entry, datetime.now()) for entry in res.all_entries()
        )
        t0, t1 = as_vcs_translations(res)

        assert e0.new_key == ["No Comments or Sources"]
        assert e0.string == "Translated No Comments or Sources"
        assert e0.comment == ""
        assert e0.source == []

        assert t0.key == ("No Comments or Sources",)
        assert t0.string == "Translated No Comments or Sources"

        assert e1.new_key == ["Nested", "key"]
        assert e1.string == "value"
        assert e1.comment == ""
        assert e1.source == []

        assert t1.key == ("Nested", "key")
        assert t1.string == "value"

    def test_key_conflict(self):
        src = dedent("""
            {
                "Source": { "String": "foo" },
                "Source.String": "bar",
                "[\\"Source\\", \\"String\\"]": "eek"
            }
            """)

        res = parse_resource(Format.plain_json, src)
        e0, e1, e2 = (
            plain_json_as_entity(entry, datetime.now()) for entry in res.all_entries()
        )

        assert e0.new_key == ["Source", "String"]
        assert e0.string == "foo"

        assert e1.new_key == ["Source.String"]
        assert e1.string == "bar"

        assert e2.new_key == ['["Source", "String"]']
        assert e2.string == "eek"
