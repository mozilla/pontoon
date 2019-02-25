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
        contents = dedent("""text = Arise,awake and do not stop until the goal is reached.""")

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
        translate_resource = self.get_nonexistant_file_resource(path)
        source_resource = ftl.FTLResource(source_path, locale=None)
        ftl.parse(path, source_path=source_path, locale=None)
        assert_true(ftl.FTLResource(path, locale=None, source_resource=source_resource))

    def test_parse_with_no_source_path(self):
        contents = dedent("""text = Arise, awake and do not stop until the goal is reached.""")
        path = create_named_tempfile(
            contents,
            prefix='strings',
            suffix='.ftl',
            directory=self.tempdir,
        )
        ftl.parse(path, source_path=None, locale=None)
        assert_true(ftl.FTLResource(path, locale=None, source_resource=None))