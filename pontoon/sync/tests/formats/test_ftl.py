from textwrap import dedent
import os
import shutil
import tempfile
from django_nose.tools import (
    assert_equal,
    assert_raises,
    assert_true,
)
from pontoon.base.tests import (
    assert_attributes_equal,
    TestCase,
    create_named_tempfile,
)
from pontoon.sync.formats import ftl
from pontoon.sync.tests.formats import FormatTestsMixin

class FTLResourceTests(FormatTestsMixin, TestCase):
    parse = staticmethod(ftl.parse)
    supports_source = False
    supports_keys = False
    supports_source_string = False

    def setUp(self):
        super(FTLResourceTests, self).setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super(FTLResourceTests, self).tearDown()
        shutil.rmtree(self.tempdir)

    def get_nonexistant_file_resource(self, path):
        contents = dedent("""<?xml version="1.0" encoding="utf-8"?>
            <resources>
                <string name="source-string">Source String</string>
            </resources>
        """)

        source_path = create_named_tempfile(
            contents,
            prefix='strings',
            suffix='.ftl',
            directory=self.tempdir,
        )
        source_resource = ftl.FTLResource(source_path, locale=None)

        return ftl.FTLResource(
            path,
            locale=None,
            source_resource=source_resource,
        )

    def get_nonexistant_file_path(self):
        return os.path.join(self.tempdir, 'strings.ftl')

    def test_init_missing_resource(self):
        """
        If the FTLresource file doesn't exist and no source resource is
        given, raise a IOError.
        """
        path = self.get_nonexistant_file_path()
        with assert_raises(IOError):
            ftl.FTLResource(path, locale=None, source_resource=None)

    def test_init_missing_resource_with_source(self):
        """
        If the FTLresourcedoesn't exist but a source resource is
        given, return a resource with empty translations.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path)

        assert_equal(len(translated_resource.translations), 1)
        translation = translated_resource.translations[0]
        assert_equal(translation.strings, {})