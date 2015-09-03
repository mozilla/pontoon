from textwrap import dedent

from pontoon.base.formats import silme
from pontoon.base.tests import TestCase
from pontoon.base.tests.formats import FormatTestsMixin


BASE_DTD_FILE = """
<!-- Sample comment -->
<!ENTITY SourceString "Translated String">

<!-- First comment -->
<!-- Second comment -->
<!ENTITY MultipleComments "Translated Multiple Comments">

<!ENTITY NoCommentsorSources "Translated No Comments or Sources">
"""


class DTDTests(FormatTestsMixin, TestCase):
    parse = staticmethod(silme.parse_dtd)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """DTD keys can't contain spaces."""
        return super(DTDTests, self).key(source_string).replace(' ', '')

    def test_parse_basic(self):
        self.run_parse_basic(BASE_DTD_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_DTD_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_DTD_FILE, 2)

    def test_save_basic(self):
        input_string = dedent("""
            <!-- Comment -->
            <!ENTITY SourceString "Source String">
        """)
        expected_string = dedent("""
            <!-- Comment -->
            <!ENTITY SourceString "New Translated String">
        """)

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """Deleting strings removes them completely from the DTD file."""
        input_string = dedent("""
            <!-- Comment -->
            <!ENTITY SourceString "Source String">
        """)
        expected_string = dedent("""
            <!-- Comment -->
        """)

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent("""
            <!ENTITY SourceString "Source String">
        """)
        input_string = dedent("""
            <!ENTITY MissingSourceString "Translated Missing String">
            <!ENTITY SourceString "Translated String">
        """)
        expected_string = dedent("""
            <!ENTITY SourceString "Translated String">
        """)

        self.run_save_source_no_changes(source_string, input_string, expected_string)

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent("""
            <!ENTITY SourceString "Source String">
            <!ENTITY OtherSourceString "Other String">
        """)
        input_string = dedent("""
            <!ENTITY OtherSourceString "Translated Other String">
        """)

        self.run_save_source_no_changes(source_string, input_string, input_string)

    def test_save_translation_missing(self):
        source_string = dedent("""
            <!ENTITY String "Source String">
            <!ENTITY MissingString "Missing Source String">
        """)
        input_string = dedent("""
            <!ENTITY String "Translated String">
        """)
        expected_string = dedent("""
            <!ENTITY String "Translated String">
            <!ENTITY MissingString "Translated Missing String">
        """)

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent("""
            <!ENTITY String "Source String">
        """)
        input_string = dedent("""
            <!ENTITY String "Translated String">
        """)
        expected_string = dedent("""
            <!ENTITY String "Source String">
        """)

        self.run_save_translation_identical(source_string, input_string, expected_string)


BASE_PROPERTIES_FILE = """
# Sample comment
SourceString=Translated String

# First comment
# Second comment
MultipleComments=Translated Multiple Comments

NoCommentsorSources=Translated No Comments or Sources
"""


class PropertiesTests(FormatTestsMixin, TestCase):
    parse = staticmethod(silme.parse_properties)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """Properties keys can't contain spaces."""
        return super(PropertiesTests, self).key(source_string).replace(' ', '')

    def test_parse_basic(self):
        self.run_parse_basic(BASE_PROPERTIES_FILE, 0)

    def test_parse_multiple_comments(self):
        #import ipdb; ipdb.set_trace()
        self.run_parse_multiple_comments(BASE_PROPERTIES_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_PROPERTIES_FILE, 2)

    def test_save_basic(self):
        input_string = dedent("""
            # Comment
            SourceString=Source String
        """)
        expected_string = dedent("""
            # Comment
            SourceString=New Translated String
        """)

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """
        Deleting strings removes them completely from the properties
        file.
        """
        input_string = dedent("""
            # Comment
            SourceString=Source String
        """)
        expected_string = dedent("""
            # Comment
        """)

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent("""
            SourceString=Source String
        """)
        input_string = dedent("""
            MissingSourceString=Translated Missing String
            SourceString=Translated String
        """)
        expected_string = dedent("""
            SourceString=Translated String
        """)

        self.run_save_source_no_changes(source_string, input_string, expected_string)

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent("""
            SourceString=Source String
            OtherSourceString=Other String
        """)
        input_string = dedent("""
            OtherSourceString=Translated Other String
        """)

        self.run_save_source_no_changes(source_string, input_string, input_string)

    def test_save_translation_missing(self):
        source_string = dedent("""
            String=Source String
            MissingString=Missing Source String
        """)
        input_string = dedent("""
            String=Translated String
        """)
        expected_string = dedent("""
            String=Translated String
            MissingString=Translated Missing String
        """)

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent("""
            String=Source String
        """)
        input_string = dedent("""
            String=Translated String
        """)
        expected_string = dedent("""
            String=Source String
        """)

        self.run_save_translation_identical(source_string, input_string, expected_string)


BASE_INI_FILE = """
[Strings]
# Sample comment
SourceString=Translated String

# First comment
# Second comment
MultipleComments=Translated Multiple Comments

NoCommentsorSources=Translated No Comments or Sources
"""


class IniTests(FormatTestsMixin, TestCase):
    parse = staticmethod(silme.parse_properties)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """Ini keys can't contain spaces."""
        return super(IniTests, self).key(source_string).replace(' ', '')

    def test_parse_basic(self):
        self.run_parse_basic(BASE_INI_FILE, 0)

    def test_parse_multiple_comments(self):
        #import ipdb; ipdb.set_trace()
        self.run_parse_multiple_comments(BASE_INI_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_INI_FILE, 2)

    def test_save_basic(self):
        input_string = dedent("""
            [Strings]
            # Comment
            SourceString=Source String
        """)
        expected_string = dedent("""
            [Strings]
            # Comment
            SourceString=New Translated String
        """)

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """
        Deleting strings removes them completely from the ini file.
        """
        input_string = dedent("""
            [Strings]
            # Comment
            SourceString=Source String
        """)
        expected_string = dedent("""
            [Strings]
            # Comment
        """)

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent("""
            [Strings]
            SourceString=Source String
        """)
        input_string = dedent("""
            [Strings]
            MissingSourceString=Translated Missing String
            SourceString=Translated String
        """)
        expected_string = dedent("""
            [Strings]
            SourceString=Translated String
        """)

        self.run_save_source_no_changes(source_string, input_string, expected_string)

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent("""
            [Strings]
            SourceString=Source String
            OtherSourceString=Other String
        """)
        input_string = dedent("""
            [Strings]
            OtherSourceString=Translated Other String
        """)

        self.run_save_source_no_changes(source_string, input_string, input_string)

    def test_save_translation_missing(self):
        source_string = dedent("""
            [Strings]
            String=Source String
            MissingString=Missing Source String
        """)
        input_string = dedent("""
            [Strings]
            String=Translated String
        """)
        expected_string = dedent("""
            [Strings]
            String=Translated String
            MissingString=Translated Missing String
        """)

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent("""
            [Strings]
            String=Source String
        """)
        input_string = dedent("""
            [Strings]
            String=Translated String
        """)
        expected_string = dedent("""
            [Strings]
            String=Source String
        """)

        self.run_save_translation_identical(source_string, input_string, expected_string)
