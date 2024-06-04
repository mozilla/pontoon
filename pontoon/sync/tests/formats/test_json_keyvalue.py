from pontoon.base.tests import TestCase, assert_attributes_equal
from pontoon.sync.formats import json_keyvalue
from pontoon.sync.tests.formats import FormatTestsMixin
from textwrap import dedent


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
        path, resource = self.parse_string(BASE_JSON_FILE)
        assert_attributes_equal(
            resource.translations[0],
            comments=[],
            source=[],
            key=self.key('["No Comments or Sources"]'),
            strings={None: "Translated No Comments or Sources"},
            source_string_plural="",
            fuzzy=False,
            order=0,
        )

    # Validate nested values internal key format
    def test_parse_nested(self):
        path, resource = self.parse_string(BASE_JSON_FILE)
        assert_attributes_equal(
            resource.translations[1],
            comments=[],
            source=[],
            # Nested keys are internally using "\200" as a separator
            key=self.key('["Nested", "key"]'),
            strings={None: "value"},
            fuzzy=False,
            order=1,
        )

    # Check if using a dot key do not mess with nested values
    def test_save_non_nested_dot_key(self):
        input_string = dedent(
            """
            {
              "Source.String": "Source String"
            }
        """
        )
        expected_string = dedent(
            """
            {
              "Source.String": "New Translated String"
            }
        """
        )

        self.run_save_basic(
            input_string,
            expected_string,
            source_string=input_string,
        )

    def test_save_basic_nested(self):
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
            input_string,
            expected_string,
            source_string=input_string,
        )

    def test_save_deep__nested(self):
        input_string = dedent(
            """
            {
              "Source": {
                "String": {
                  "Deeply": {
                    "Nested": "Source String"
                  }
                }
              }
            }
        """
        )
        expected_string = dedent(
            """
            {
              "Source": {
                "String": {
                  "Deeply": {
                    "Nested": "New Translated String"
                  }
                }
              }
            }
        """
        )

        self.run_save_basic(
            input_string,
            expected_string,
            source_string=input_string,
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
            input_string,
            expected_string,
            source_string=input_string,
        )

    # Validate if the key is formated in json and context in dot representation
    def test_key_and_context_format(self):
        input_string = dedent(
            """
            {
                "Source": {
                  "String": "Source String"
                }
            }
        """
        )
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[0],
            key='["Source", "String"]',
            context="Source.String",
        )

    # Validate if we can use JSON looking keys
    def test_json_key(self):
        input_string = dedent(
            """
            {
                "[\\"Source\\", \\"String\\"]": "Source String"
            }
        """
        )
        expected_string = dedent(
            """
            {
              "[\\"Source\\", \\"String\\"]": "New Translated String"
            }
        """
        )

        self.run_save_basic(
            input_string,
            expected_string,
            source_string=input_string,
        )

    def test_key_conflict(self):
        input_string = dedent(
            """
          {
            "Source": { "String": "foo" },
            "Source.String": "bar",
            "[\\"Source\\", \\"String\\"]": "eek"
          }
      """
        )

        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[0],
            key='["Source", "String"]',
            context="Source.String",
            strings={None: "foo"},
        )
        assert_attributes_equal(
            resource.translations[1],
            key='["Source.String"]',
            context="Source.String",
            strings={None: "bar"},
        )
        assert_attributes_equal(
            resource.translations[2],
            key='["[\\"Source\\", \\"String\\"]"]',
            context='["Source", "String"]',
            strings={None: "eek"},
        )
