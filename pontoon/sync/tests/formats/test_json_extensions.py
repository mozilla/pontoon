from datetime import datetime
from textwrap import dedent
from unittest import TestCase

from moz.l10n.formats import Format
from moz.l10n.resource import parse_resource

from pontoon.sync.formats import as_entity, as_vcs_translations


class JsonExtensionsTests(TestCase):
    def test_webext(self):
        src = dedent("""
            {
              "SourceString": {
                "message": "Translated String",
                "description": "Sample comment"
              },

              "MultipleComments": {
                "message": "Translated Multiple Comments",
                "description": "First comment",
                "description": "Second comment"
              },

              "NoCommentsorSources": {
                "message": "Translated No Comments or Sources"
              },

              "placeholder": {
                "message": "Hello $YOUR_NAME$",
                "description": "Peer greeting",
                "placeholders": {
                  "your_name": {
                    "content": "$1",
                    "example": "Cira"
                  }
                }
              }
            }
            """)

        res = parse_resource(Format.webext, src)
        e0, e1, e2, e3 = (
            as_entity(Format.webext, (), entry, date_created=datetime.now())
            for entry in res.all_entries()
        )
        t0, t1, t2, t3 = as_vcs_translations(res)

        assert e0.comment == "Sample comment"
        assert t0.string == "Translated String"

        assert e1.comment == "Second comment"

        assert t2.string == "Translated No Comments or Sources"

        assert e3.key == ["placeholder"]
        assert e3.string == "Hello $YOUR_NAME$"
        assert e3.comment == "Peer greeting"
        assert e3.meta == [
            ["placeholders", '{"YOUR_NAME": {"content": "$1", "example": "Cira"}}'],
        ]

        assert t3.key == ("placeholder",)
        assert t3.string == "Hello $YOUR_NAME$"
