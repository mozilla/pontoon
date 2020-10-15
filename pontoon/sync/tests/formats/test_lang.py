import os.path
from textwrap import dedent

import pytest

from pontoon.base.tests import assert_attributes_equal, TestCase
from pontoon.sync.exceptions import ParseError
from pontoon.sync.formats import lang
from pontoon.sync.tests.formats import FormatTestsMixin


BASE_LANG_FILE = """
# Sample comment
;Source String
Translated String

# First comment
# Second comment
;Multiple Comments
Translated Multiple Comments

;No Comments or Sources
Translated No Comments or Sources
"""


class LangTests(FormatTestsMixin, TestCase):
    parse = staticmethod(lang.parse)
    supports_source = False
    supports_keys = False
    supports_source_string = True

    def test_parse_basic(self):
        self.run_parse_basic(BASE_LANG_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_LANG_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_LANG_FILE, 2)

    def test_save_basic(self):
        input_string = dedent(
            """
            # Comment
            ;SourceString
            Source String
        """
        )
        expected_string = dedent(
            """
            # Comment
            ;SourceString
            New Translated String
        """
        )

        self.run_save_basic(input_string, expected_string)

    def test_save_remove(self):
        """
        Deleting strings shouled replace the translation with the source
        string.
        """
        input_string = dedent(
            """
            # Comment
            ;SourceString
            Translated String
        """
        )
        expected_string = dedent(
            """
            # Comment
            ;SourceString
            SourceString
        """
        )

        self.run_save_remove(input_string, expected_string)

    def test_load_utf8_bom(self):
        """
        Ensure that the langfile parser can load UTF-8 files with an encoded
        BOM at the beginning of the file.

        See https://docs.python.org/2/library/codecs.html for details (search
        for the string "utf-8-sig").
        """
        current_dir = os.path.dirname(__file__)
        resource = lang.parse(os.path.join(current_dir, "bom.lang"))
        assert len(resource.translations) == 1
        assert_attributes_equal(
            resource.translations[0],
            source_string="Source String",
            strings={None: "Translated String"},
        )

    def test_parse_comments_arbitrary_hash(self):
        """Comments can have an arbitrary amount of #s at the start."""
        path, resource = self.parse_string(
            dedent(
                """
            # 1 hash
            ## 2 hash
            ### 3 hash

            # 1 hash
            ## 2 hash
            ### 3 hash
            ; Source
            Translated
        """
            )
        )

        assert resource.children[1].content == "1 hash"
        assert resource.children[2].content == "2 hash"
        assert resource.children[3].content == "3 hash"
        assert resource.translations[0].comments == ["1 hash", "2 hash", "3 hash"]

    def test_parse_eof(self):
        """Langfiles do not need to end in a newline."""
        path, resource = self.parse_string(";Source\nTranslation")
        assert resource.translations[0].source_string == "Source"
        assert resource.translations[0].strings == {None: "Translation"}

    def test_preserve_comment_hashes(self):
        """
        If a langfile is parsed and then saved without being modified,
        it should not modify the contents of the file.
        """
        expected = dedent(
            """
            ## Example langfile with a few constructs that might break

            # Entity comment
            ;Source
            Translated

            # Single hash standalone comment

            ### Entity comment with multiple hashes
            ;Identical
            Identical {ok}

            ###Free standing comment at the end. WOW
        """
        )
        path, resource = self.parse_string(expected)
        resource.save(self.locale)
        self.assert_file_content(path, expected)

    def test_parse_empty_translation(self):
        """
        If an entity has an empty translation, parse should raise a
        ParseError.
        """
        with pytest.raises(ParseError):
            self.parse_string(
                dedent(
                    """
                # Comment
                ;Source
                Translated

                ;Empty

                ;Not Empty
                Nope
            """
                )
            )
