from textwrap import dedent

from pontoon.base.tests import TestCase
from pontoon.sync.formats import json_keyvalue
from pontoon.sync.tests.formats import FormatTestsMixin

from pontoon.base.tests import assert_attributes_equal

BASE_JSON_FILE = """
{
  "No Comments or Sources": "Translated No Comments or Sources",
  "Nested": {
    "key": "value"
  }
}
"""


class JsonKeyValueTests(FormatTestsMixin, TestCase):
    parse = staticmethod(json_keyvalue.parse)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_JSON_FILE, 0)

    def test_parse_nested(self):
        path, resource = self.parse_string(BASE_JSON_FILE)
        assert_attributes_equal(
            resource.translations[1],
            comments=[],
            source=[],
            key=self.key("Nested.key"),
            strings={None: "value"},
            fuzzy=False,
            order=0,
        )

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
