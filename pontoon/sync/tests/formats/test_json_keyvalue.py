from textwrap import dedent

from pontoon.base.tests import assert_attributes_equal, TestCase
from pontoon.sync.formats import json_keyvalue
from pontoon.sync.tests.formats import FormatTestsMixin


BASE_JSON_FILE = """
{
  "No": {
    "Comments": {
      "or": {
        "Sources": "Translated No Comments or Sources"
      }
    }
  }
}
"""


class JsonKeyValueTests(FormatTestsMixin, TestCase):
    parse = staticmethod(json_keyvalue.parse)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """JSON keys can't contain spaces."""
        return super().key(source_string).replace(" ", ".")

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_JSON_FILE, 0)

    def test_save_basic(self):
        input_string = dedent(
            """
            {
              "Source": {
                "String": "Source String"
              }
            }
        """
        )
        expected_string = dedent(
            """
            {
              "Source": {
                "String": "New Translated String"
              }
            }
        """
        )

        self.run_save_basic(
            input_string, expected_string, source_string=input_string,
        )

    def test_save_remove(self):
        input_string = dedent(
            """
            {
                "Source": {
                  "String": "Source String"
                }
            }
        """
        )
        expected_string = dedent(
            """
            {}
        """
        )

        self.run_save_remove(
            input_string, expected_string, source_string=input_string,
        )
