from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from pontoon.sync.formats import parse_translations


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

        with TemporaryDirectory() as dir:
            path = join(dir, "messages.json")
            with open(path, "x") as file:
                file.write(src)
            t0, t1, t2, t3 = parse_translations(path)

        assert t0.string == "Translated String"
        assert t0.comments == ["Sample comment"]

        assert t1.comments == ["Second comment"]

        assert t2.string == "Translated No Comments or Sources"

        assert t3.key == "placeholder"
        assert t3.string == "Hello $YOUR_NAME$"
        assert t3.comments == ["Peer greeting"]
        assert t3.source == {"YOUR_NAME": {"content": "$1", "example": "Cira"}}
        assert t3.order == 3
