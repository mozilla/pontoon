import os
import shutil
import tempfile

from textwrap import dedent

from django_nose.tools import (
    assert_equal,
    assert_raises,
    assert_true,
)
from pontoon.base.tests import (
    TestCase,
    create_named_tempfile,
    LocaleFactory,
)
from pontoon.sync.formats import ftl
from pontoon.sync.tests.formats import FormatTestsMixin


class FTLResourceTests(FormatTestsMixin, TestCase):
    def setUp(self):
        super(FTLResourceTests, self).setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super(FTLResourceTests, self).tearDown()
        shutil.rmtree(self.tempdir)

    def get_nonexistant_file_resource(self, path):
        contents = dedent("""text = Arise, awake and do not stop until the goal is reached.""")

        source_path = create_named_tempfile(
            contents,
            prefix='strings',
            suffix='.ftl',
            directory=self.tempdir,
        )
        source_resource = ftl.FTLResource(path=source_path, locale=None, source_resource=None)

        return ftl.FTLResource(
            path,
            locale=None,
            source_resource=source_resource,
        )

    def get_nonexistant_file_path(self):
        return os.path.join(self.tempdir, 'strings.ftl')

    def test_init_missing_resource(self):
        """
        If the FTLResource file doesn't exist and no source resource is
        given, raise a IOError.
        """
        path = self.get_nonexistant_file_path()
        with assert_raises(IOError):
            ftl.FTLResource(path, locale=None, source_resource=None)

    def test_init_missing_resource_with_source(self):
        """
        If the FTLResource doesn't exist but a source resource is
        given, return a resource with empty translations.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path)

        assert_equal(len(translated_resource.translations), 1)
        translation = translated_resource.translations[0]
        assert_equal(translation.strings, {})

    def test_save_create_dirs(self):
        """
        If the directories in a resource's path don't exist, create them on
        save.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path)

        translated_resource.translations[0].strings = {
            None: 'New Translated String'
        }
        translated_resource.save(LocaleFactory.create())
        assert_true(os.path.exists(path))

    def test_parse_with_source_path(self):
        contents = dedent("""text = Arise, awake and do not stop until the goal is reached.""")
        source_path = create_named_tempfile(
            contents,
            prefix='strings',
            suffix='.ftl',
            directory=self.tempdir,
        )
        path = self.get_nonexistant_file_path()
        obj = ftl.parse(path, source_path=source_path, locale=None)
        assert_equal(obj.path, path)
        assert_equal(obj.locale, None)
        assert_equal(obj.source_resource.path, source_path)
        assert_equal(obj.source_resource.locale, None)

    def test_parse_with_no_source_path(self):
        contents = dedent("""text = Arise, awake and do not stop until the goal is reached.""")
        path = create_named_tempfile(
            contents,
            prefix='strings',
            suffix='.ftl',
            directory=self.tempdir,
        )
        obj = ftl.parse(path, source_path=None, locale=None)
        assert_equal(obj.path, path)
        assert_equal(obj.source_resource, None)
        assert_equal(obj.locale, None)


BASE_ANDROID_FTL_FILE = """
# Sample comment
Source-String = Translated String

# First comment
# Second comment
Multiple-Comments = Translated Multiple Comments

No-Comments-or-Sources = Translated No Comments or Sources
Empty-Translation =
"""


class AndroidFTLTests(FormatTestsMixin, TestCase):
    parse = staticmethod(ftl.parse)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def setUp(self):
        super(AndroidFTLTests, self).setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super(AndroidFTLTests, self).tearDown()
        shutil.rmtree(self.tempdir)

    def parse_string(
        self,
        string,
        source_string=None,
        locale=None,
        path=None,
        source_path=None,
    ):
        """Android FTL files must contain the word 'strings'."""
        path = create_named_tempfile(
            string,
            prefix='strings',
            suffix='.ftl',
            directory=self.tempdir,
        )
        if source_string is not None:
            source_path = create_named_tempfile(
                source_string,
                prefix='strings',
                suffix='.ftl',
                directory=self.tempdir,
            )
        return super(AndroidFTLTests, self).parse_string(
            string,
            source_string=source_string,
            locale=locale,
            path=path,
            source_path=source_path,
        )

    # def test_parse_basic(self):
    #     self.run_parse_basic(BASE_ANDROID_FTL_FILE, 0)

    # def test_parse_multiple_comments(self):
    #     self.run_parse_multiple_comments(BASE_ANDROID_FTL_FILE, 1)

    # def test_parse_no_comments_no_sources(self):
    #     self.run_parse_no_comments_no_sources(BASE_ANDROID_FTL_FILE, 2)

    # def test_parse_empty_translation(self):
    #     self.run_parse_empty_translation(BASE_ANDROID_FTL_FILE, 3)

    def test_save_basic(self):
        input_string = dedent("""Source-String = Source String""")
        expected_string = dedent("""""")

        self.run_save_basic(input_string, expected_string, source_string=input_string)

    def test_save_remove(self):
        """Deleting strings removes them completely from the FTL file."""
        input_string = dedent("""Source-String = Source String""")
        expected_string = dedent("""
        """)

        self.run_save_remove(input_string, expected_string, source_string=input_string)

    def test_save_source_removed(self):
        """
        If an entity is missing from the source resource, remove it from
        the translated resource.
        """
        source_string = dedent("""Source-String = Source String""")
        input_string = dedent("""
Missing-Source-String = Translated Missing String
Source-String = Translated String
        """)
        expected_string = dedent("""Source-String = Translated String""")

        self.run_save_no_changes(input_string, expected_string, source_string=source_string)

    def test_save_source_no_translation(self):
        """
        If an entity is missing from the translated resource and has no
        translation, do not add it back in.
        """
        source_string = dedent("""
Source-String = Source String
Other-Source-String = Other String
        """)
        input_string = dedent("""Other-Source-String = Translated Other String""")

        self.run_save_no_changes(input_string, input_string, source_string=source_string)

#     def test_save_translation_missing(self):
#         source_string = dedent("""String = Source String
# Missing-String = Missing Source String
#         """)
#         input_string = dedent("""String = Translated String""")
#         expected_string = dedent("""String = Translated String
# Missing-String = Translated Missing String
#         """)

        self.run_save_translation_missing(source_string, input_string, expected_string)

    def test_save_translation_identical(self):
        source_string = dedent("""String = Source String""")
        input_string = dedent("""String = Translated String""")
        expected_string = dedent("""""")

        self.run_save_translation_identical(source_string, input_string, expected_string)
