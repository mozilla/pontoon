import shutil
import tempfile

from pontoon.base.tests import TestCase, assert_attributes_equal, create_named_tempfile
from pontoon.sync.formats import ftl
from pontoon.sync.tests.formats import FormatTestsMixin


class FTLResourceTests(FormatTestsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tempdir)

    def test_parse_with_no_source_path(self):
        contents = "text = Arise, awake and do not stop until the goal is reached."
        path = create_named_tempfile(
            contents,
            prefix="strings",
            suffix=".ftl",
            directory=self.tempdir,
        )
        assert ftl.parse(path)


BASE_FTL_FILE = """
# Sample comment
SourceString = Translated String

# First comment
# Second comment
MultipleComments = Translated Multiple Comments

NoCommentsOrSources = Translated No Comments or Sources
"""


class FTLTests(FormatTestsMixin, TestCase):
    parse = staticmethod(ftl.parse)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tempdir)

    def key(self, source_string):
        """FTL keys can't contain spaces."""
        return super().key(source_string).replace(" ", "")

    def test_parse_basic(self):
        input_string = BASE_FTL_FILE
        translation_index = 0
        _, translations = self.parse_string(input_string)

        assert_attributes_equal(
            translations[translation_index],
            comments=["Sample comment"],
            key=self.key("Source String"),
            strings={None: "SourceString = Translated String\n"},
            fuzzy=False,
            order=translation_index,
        )

    def test_parse_multiple_comments(self):
        input_string = BASE_FTL_FILE
        translation_index = 1
        _, translations = self.parse_string(input_string)

        assert_attributes_equal(
            translations[translation_index],
            comments=["First comment\nSecond comment"],
            source=[],
            key=self.key("Multiple Comments"),
            strings={None: "MultipleComments = Translated Multiple Comments\n"},
            fuzzy=False,
            order=translation_index,
        )

    def test_parse_no_comments_no_sources(self):
        input_string = BASE_FTL_FILE
        translation_index = 2
        _, translations = self.parse_string(input_string)

        assert_attributes_equal(
            translations[translation_index],
            comments=[],
            source=[],
            key=self.key("No Comments Or Sources"),
            strings={None: "NoCommentsOrSources = Translated No Comments or Sources\n"},
            fuzzy=False,
            order=translation_index,
        )
