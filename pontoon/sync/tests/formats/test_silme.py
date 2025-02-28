from textwrap import dedent

from pontoon.base.tests import TestCase, assert_attributes_equal
from pontoon.sync.formats import silme
from pontoon.sync.tests.formats import FormatTestsMixin


BASE_DTD_FILE = """
<!-- Sample comment -->
<!ENTITY SourceString "Translated String">

<!-- First comment -->
<!-- Second comment -->
<!ENTITY MultipleComments "Translated Multiple Comments">

<!ENTITY NoCommentsorSources "Translated No Comments or Sources">

<!ENTITY EmptyTranslation "">
"""


class DTDTests(FormatTestsMixin, TestCase):
    parse = staticmethod(silme.parse_dtd)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """DTD keys can't contain spaces."""
        return super().key(source_string).replace(" ", "")

    def test_parse_basic(self):
        self.run_parse_basic(BASE_DTD_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_DTD_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_DTD_FILE, 2)

    def test_parse_empty_translation(self):
        self.run_parse_empty_translation(BASE_DTD_FILE, 3)


BASE_PROPERTIES_FILE = """
# Sample comment
SourceString=Translated String

# First comment
# Second comment
MultipleComments=Translated Multiple Comments

NoCommentsorSources=Translated No Comments or Sources

EmptyTranslation=
"""


class PropertiesTests(FormatTestsMixin, TestCase):
    parse = staticmethod(silme.parse_properties)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """Properties keys can't contain spaces."""
        return super().key(source_string).replace(" ", "")

    def test_parse_basic(self):
        self.run_parse_basic(BASE_PROPERTIES_FILE, 0)

    def test_parse_multiple_comments(self):
        # import ipdb; ipdb.set_trace()
        self.run_parse_multiple_comments(BASE_PROPERTIES_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_PROPERTIES_FILE, 2)

    def test_parse_empty_translation(self):
        self.run_parse_empty_translation(BASE_PROPERTIES_FILE, 3)


BASE_INI_FILE = """
[Strings]
# Sample comment
SourceString=Translated String

# First comment
# Second comment
MultipleComments=Translated Multiple Comments

NoCommentsorSources=Translated No Comments or Sources

EmptyTranslation=
"""


class IniTests(FormatTestsMixin, TestCase):
    parse = staticmethod(silme.parse_properties)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """Ini keys can't contain spaces."""
        return super().key(source_string).replace(" ", "")

    def test_parse_basic(self):
        self.run_parse_basic(BASE_INI_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_INI_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_INI_FILE, 2)

    def test_parse_empty_translation(self):
        self.run_parse_empty_translation(BASE_INI_FILE, 3)


BASE_INC_FILE = """
# Sample comment
#define SourceString Translated String

# First comment
# Second comment
#define MultipleComments Translated Multiple Comments

#define NoCommentsorSources Translated No Comments or Sources

#define EmptyTranslation
"""


class IncTests(FormatTestsMixin, TestCase):
    parse = staticmethod(silme.parse_inc)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """Inc keys can't contain spaces."""
        return super().key(source_string).replace(" ", "")

    def test_parse_basic(self):
        self.run_parse_basic(BASE_INC_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_INC_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_INC_FILE, 2)

    def test_parse_empty_translation(self):
        self.run_parse_empty_translation(BASE_INC_FILE, 3)

    def test_moz_langpack_contributors(self):
        """
        If a .inc file has a commented-out entity named
        MOZ_LANGPACK_CONTRIBUTORS, the parser should un-comment it and
        process it as an entity.
        """
        input_string = dedent(
            """
            #define String Some String

            # #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
        )

        _, translations = self.parse_string(input_string)
        assert len(translations) == 2
        assert_attributes_equal(
            translations[1],
            key="MOZ_LANGPACK_CONTRIBUTORS",
            strings={None: "Contributor list"},
        )

    def test_moz_langpack_contributors_comment(self):
        input_string = dedent(
            """
            #define String Some String

            # #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
        )
        _, translations = self.parse_string(input_string)
        assert len(translations) == 2
        assert_attributes_equal(
            translations[1],
            key="MOZ_LANGPACK_CONTRIBUTORS",
            strings={None: "Contributor list"},
        )

    def test_moz_langpack_contributors_actual(self):
        input_string = dedent(
            """
            #define String Translated String

            #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
        )

        _, translations = self.parse_string(input_string)
        assert len(translations) == 2
        assert_attributes_equal(
            translations[1],
            key="MOZ_LANGPACK_CONTRIBUTORS",
            strings={None: "Contributor list"},
        )
