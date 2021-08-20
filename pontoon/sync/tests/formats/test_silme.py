import os.path
import tempfile
from textwrap import dedent

import pytest
from silme.format.dtd import FormatParser as DTDParser

from pontoon.base.tests import (
    assert_attributes_equal,
    create_tempfile,
    LocaleFactory,
    TestCase,
)
from pontoon.sync.exceptions import ParseError
from pontoon.sync.formats import silme
from pontoon.sync.tests.formats import FormatTestsMixin


class SilmeResourceTests(TestCase):
    def test_init_missing_resource(self):
        """
        If the translated resource doesn't exist and no source resource
        is given, raise a ParseError.
        """
        path = os.path.join(tempfile.mkdtemp(), "does", "not", "exist.dtd")
        with pytest.raises(ParseError):
            silme.SilmeResource(DTDParser, path, source_resource=None)

    def create_nonexistant_resource(self, path):
        source_path = create_tempfile(
            dedent(
                """
            <!ENTITY SourceString "Source String">
        """
            )
        )
        source_resource = silme.SilmeResource(DTDParser, source_path)

        return silme.SilmeResource(DTDParser, path, source_resource=source_resource)

    def test_init_missing_resource_with_source(self):
        """
        If the translated resource doesn't exist but a source resource
        is given, return a resource with empty translations.
        """
        path = os.path.join(tempfile.mkdtemp(), "does", "not", "exist.dtd")
        translated_resource = self.create_nonexistant_resource(path)

        assert len(translated_resource.translations) == 1
        assert translated_resource.translations[0].strings == {}

    def test_save_create_dirs(self):
        """
        If the directories in a resource's path don't exist, create them
        on save.
        """
        path = os.path.join(tempfile.mkdtemp(), "does", "not", "exist.dtd")
        translated_resource = self.create_nonexistant_resource(path)

        translated_resource.translations[0].strings = {None: "New Translated String"}
        translated_resource.save(LocaleFactory.create())

        assert os.path.exists(path)


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

    def test_save_basic(self):
        input_string = dedent(
            """
            <!-- Comment -->
            <!ENTITY SourceString "Source String">
        """
        )
        expected_string = dedent(
            """
            <!-- Comment -->
            <!ENTITY SourceString "New Translated String">
        """
        )

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """Deleting strings removes them completely from the DTD file."""
        input_string = dedent(
            """
            <!-- Comment -->
            <!ENTITY SourceString "Source String">
        """
        )
        expected_string = dedent(
            """
            <!-- Comment -->
        """
        )

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent(
            """
            <!ENTITY SourceString "Source String">
        """
        )
        input_string = dedent(
            """
            <!ENTITY MissingSourceString "Translated Missing String">
            <!ENTITY SourceString "Translated String">
        """
        )
        expected_string = dedent(
            """
            <!ENTITY SourceString "Translated String">
        """
        )

        self.run_save_no_changes(
            input_string, expected_string, source_string=source_string
        )

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent(
            """
            <!ENTITY SourceString "Source String">
            <!ENTITY OtherSourceString "Other String">
        """
        )
        input_string = dedent(
            """
            <!ENTITY OtherSourceString "Translated Other String">
        """
        )

        self.run_save_no_changes(
            input_string, input_string, source_string=source_string
        )

    def test_save_translation_missing(self):
        source_string = dedent(
            """
            <!ENTITY String "Source String">
            <!ENTITY MissingString "Missing Source String">
        """
        )
        input_string = dedent(
            """
            <!ENTITY String "Translated String">
        """
        )
        expected_string = dedent(
            """
            <!ENTITY String "Translated String">
            <!ENTITY MissingString "Translated Missing String">
        """
        )

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent(
            """
            <!ENTITY String "Source String">
        """
        )
        input_string = dedent(
            """
            <!ENTITY String "Translated String">
        """
        )
        expected_string = dedent(
            """
            <!ENTITY String "Source String">
        """
        )

        self.run_save_translation_identical(
            source_string, input_string, expected_string
        )

    def test_quotes(self):
        input_strings = dedent(
            """
            <!ENTITY SingleQuote "\'">
            <!ENTITY SingleQuoteHTMLEntity "\\&apos;">
            <!ENTITY SingleQuoteUnicode "\\u0027">
            <!ENTITY DoubleQuote '\\"'>
            <!ENTITY DoubleQuoteHTMLEntity "\\&quot;">
            <!ENTITY DoubleQuoteUnicode "\\u0022">
        """
        )

        # Make sure path contains 'mobile/android/base'
        dirname = os.path.join(tempfile.mkdtemp(), "mobile", "android", "base")
        os.makedirs(dirname)

        fd, path = tempfile.mkstemp(dir=dirname)
        with os.fdopen(fd, "w") as f:
            f.write(input_strings)

        resource = self.parse(path)

        # Unescape quotes when parsing
        assert_attributes_equal(resource.translations[0], strings={None: "'"})
        assert_attributes_equal(resource.translations[1], strings={None: "'"})
        assert_attributes_equal(resource.translations[2], strings={None: "'"})
        assert_attributes_equal(resource.translations[3], strings={None: '"'})
        assert_attributes_equal(resource.translations[4], strings={None: '"'})
        assert_attributes_equal(resource.translations[5], strings={None: '"'})

        # Escape quotes when saving
        translated_resource = silme.SilmeResource(
            DTDParser, path, source_resource=resource
        )
        translated_resource.translations[0].strings[None] = "Single Quote '"
        translated_resource.translations[3].strings[None] = 'Double Quote "'

        translated_resource.save(self.locale)

        expected_string = dedent(
            """
            <!ENTITY SingleQuote "Single Quote \\&apos;">
            <!ENTITY SingleQuoteHTMLEntity "\\&apos;">
            <!ENTITY SingleQuoteUnicode "\\&apos;">
            <!ENTITY DoubleQuote 'Double Quote \\&quot;'>
            <!ENTITY DoubleQuoteHTMLEntity "\\&quot;">
            <!ENTITY DoubleQuoteUnicode "\\&quot;">
        """
        )
        self.assert_file_content(path, expected_string)


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

    def test_save_basic(self):
        input_string = dedent(
            """
            # Comment
            SourceString=Source String
        """
        )
        expected_string = dedent(
            """
            # Comment
            SourceString=New Translated String
        """
        )

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """
        Deleting strings removes them completely from the properties
        file.
        """
        input_string = dedent(
            """
            # Comment
            SourceString=Source String
        """
        )
        expected_string = dedent(
            """
            # Comment
        """
        )

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent(
            """
            SourceString=Source String
        """
        )
        input_string = dedent(
            """
            MissingSourceString=Translated Missing String
            SourceString=Translated String
        """
        )
        expected_string = dedent(
            """
            SourceString=Translated String
        """
        )

        self.run_save_no_changes(
            input_string, expected_string, source_string=source_string
        )

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent(
            """
            SourceString=Source String
            OtherSourceString=Other String
        """
        )
        input_string = dedent(
            """
            OtherSourceString=Translated Other String
        """
        )

        self.run_save_no_changes(
            input_string, input_string, source_string=source_string
        )

    def test_save_translation_missing(self):
        source_string = dedent(
            """
            String=Source String
            MissingString=Missing Source String
        """
        )
        input_string = dedent(
            """
            String=Translated String
        """
        )
        expected_string = dedent(
            """
            String=Translated String
            MissingString=Translated Missing String
        """
        )

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent(
            """
            String=Source String
        """
        )
        input_string = dedent(
            """
            String=Translated String
        """
        )
        expected_string = dedent(
            """
            String=Source String
        """
        )

        self.run_save_translation_identical(
            source_string, input_string, expected_string
        )


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

    def test_save_basic(self):
        input_string = dedent(
            """
            [Strings]
            # Comment
            SourceString=Source String
        """
        )
        expected_string = dedent(
            """
            [Strings]
            # Comment
            SourceString=New Translated String
        """
        )

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """
        Deleting strings removes them completely from the ini file.
        """
        input_string = dedent(
            """
            [Strings]
            # Comment
            SourceString=Source String
        """
        )
        expected_string = dedent(
            """
            [Strings]
            # Comment
        """
        )

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent(
            """
            [Strings]
            SourceString=Source String
        """
        )
        input_string = dedent(
            """
            [Strings]
            MissingSourceString=Translated Missing String
            SourceString=Translated String
        """
        )
        expected_string = dedent(
            """
            [Strings]
            SourceString=Translated String
        """
        )

        self.run_save_no_changes(
            input_string, expected_string, source_string=source_string
        )

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent(
            """
            [Strings]
            SourceString=Source String
            OtherSourceString=Other String
        """
        )
        input_string = dedent(
            """
            [Strings]
            OtherSourceString=Translated Other String
        """
        )

        self.run_save_no_changes(
            input_string, input_string, source_string=source_string
        )

    def test_save_translation_missing(self):
        source_string = dedent(
            """
            [Strings]
            String=Source String
            MissingString=Missing Source String
        """
        )
        input_string = dedent(
            """
            [Strings]
            String=Translated String
        """
        )
        expected_string = dedent(
            """
            [Strings]
            String=Translated String
            MissingString=Translated Missing String
        """
        )

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent(
            """
            [Strings]
            String=Source String
        """
        )
        input_string = dedent(
            """
            [Strings]
            String=Translated String
        """
        )
        expected_string = dedent(
            """
            [Strings]
            String=Source String
        """
        )

        self.run_save_translation_identical(
            source_string, input_string, expected_string
        )


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

    def test_save_basic(self):
        input_string = dedent(
            """
            # Comment
            #define SourceString Source String
        """
        )
        expected_string = dedent(
            """
            # Comment
            #define SourceString New Translated String
        """
        )

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """
        Deleting strings removes them completely from the inc file.
        """
        input_string = dedent(
            """
            # Comment
            #define SourceString Source String
        """
        )
        expected_string = dedent(
            """
            # Comment
        """
        )

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent(
            """
            #define SourceString Source String
        """
        )
        input_string = dedent(
            """
            #define MissingSourceString Translated Missing String
            #define SourceString Translated String
        """
        )
        expected_string = dedent(
            """
            #define SourceString Translated String
        """
        )

        self.run_save_no_changes(
            input_string, expected_string, source_string=source_string
        )

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent(
            """
            #define SourceString Source String
            #define OtherSourceString Other String
        """
        )
        input_string = dedent(
            """
            #define OtherSourceString Translated Other String
        """
        )

        self.run_save_no_changes(
            input_string, input_string, source_string=source_string
        )

    def test_save_translation_missing(self):
        source_string = dedent(
            """
            #define String Source String
            #define MissingString Missing Source String
        """
        )
        input_string = dedent(
            """
            #define String Translated String
        """
        )
        expected_string = dedent(
            """
            #define String Translated String
            #define MissingString Translated Missing String
        """
        )

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent(
            """
            #define String Source String
        """
        )
        input_string = dedent(
            """
            #define String Translated String
        """
        )
        expected_string = dedent(
            """
            #define String Source String
        """
        )

        self.run_save_translation_identical(
            source_string, input_string, expected_string
        )

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

        path, resource = self.parse_string(input_string)
        assert len(resource.translations) == 2
        assert_attributes_equal(
            resource.translations[1],
            key="MOZ_LANGPACK_CONTRIBUTORS",
            strings={None: "Contributor list"},
        )

    def test_moz_langpack_contributors_source(self):
        """
        If a source resource was provided, meaning that we're parsing a
        translated resource, do not uncomment MOZ_LANGPACK_CONTRIBUTORS.
        """
        input_string = dedent(
            """
            #define String Some String

            # #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
        )
        source_string = dedent(
            """
            #define String Translated String

            # #define MOZ_LANGPACK_CONTRIBUTORS Other Contributors
        """
        )

        path, resource = self.parse_string(input_string, source_string=source_string)
        assert len(resource.translations) == 2
        assert_attributes_equal(
            resource.translations[1],
            key="MOZ_LANGPACK_CONTRIBUTORS",
            strings={},  # Imported from source == no translations
        )

    def test_save_moz_langpack_contributors(self):
        """
        When saving, if a translation exists for
        MOZ_LANGPACK_CONTRIBUTORS, uncomment it.
        """
        input_string = dedent(
            """
            #define String Some String

            # #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
        )
        source_string = dedent(
            """
            #define String Translated String

            # #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
        )

        path, resource = self.parse_string(input_string, source_string=source_string)
        resource.entities["MOZ_LANGPACK_CONTRIBUTORS"].strings = {
            None: "New Contributor list"
        }
        resource.save(self.locale)

        self.assert_file_content(
            path,
            dedent(
                """
            #define String Some String

            #define MOZ_LANGPACK_CONTRIBUTORS New Contributor list
        """
            ),
        )

    def test_save_moz_langpack_contributors_no_translations(self):
        """
        When saving, if a translation does not exist for
        MOZ_LANGPACK_CONTRIBUTORS, leave it commented.
        """
        input_string = dedent(
            """
            #define String Some String

            #define MOZ_LANGPACK_CONTRIBUTORS Modified contributor list
        """
        )
        source_string = dedent(
            """
            #define String Translated String

            # #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
        )

        path, resource = self.parse_string(input_string, source_string=source_string)
        resource.entities["MOZ_LANGPACK_CONTRIBUTORS"].strings = {}
        resource.save(self.locale)

        self.assert_file_content(
            path,
            dedent(
                """
            #define String Some String

            # #define MOZ_LANGPACK_CONTRIBUTORS Contributor list
        """
            ),
        )
