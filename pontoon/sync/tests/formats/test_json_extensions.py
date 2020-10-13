from textwrap import dedent

from pontoon.base.tests import assert_attributes_equal, TestCase
from pontoon.sync.formats import json_extensions
from pontoon.sync.tests.formats import FormatTestsMixin


BASE_JSON_FILE = """
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
"""


class JsonExtensionsTests(FormatTestsMixin, TestCase):
    parse = staticmethod(json_extensions.parse)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """JSON keys can't contain spaces."""
        return super(JsonExtensionsTests, self).key(source_string).replace(" ", "")

    def test_parse_basic(self):
        self.run_parse_basic(BASE_JSON_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(
            BASE_JSON_FILE, 1, comments=["Second comment"],
        )

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_JSON_FILE, 2)

    def test_parse_placeholder(self):
        input_string = BASE_JSON_FILE
        translation_index = 3
        path, resource = self.parse_string(input_string)
        assert_attributes_equal(
            resource.translations[translation_index],
            comments=["Peer greeting"],
            source={"your_name": {"content": "$1", "example": "Cira"}},
            key=self.key("placeholder"),
            strings={None: "Hello $YOUR_NAME$"},
            fuzzy=False,
            order=translation_index,
        )

    def test_save_basic(self):
        input_string = dedent(
            """
            {
              "SourceString": {
                "message": "Source String",
                "description": "Comment"
              }
            }
        """
        )
        expected_string = dedent(
            """
            {
              "SourceString": {
                "message": "New Translated String",
                "description": "Comment"
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
                "SourceString": {
                    "message": "Source String",
                    "description": "Comment"
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
