import os
import shutil
import tempfile

from textwrap import dedent

import pytest

from pontoon.base.tests import (
    TestCase,
    assert_attributes_equal,
    create_named_tempfile,
)
from pontoon.sync.formats import xml
from pontoon.sync.formats.common import ParseError
from pontoon.sync.tests.formats import FormatTestsMixin


class XMLResourceTests(TestCase):
    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tempdir)

    def get_invalid_file_path(self):
        return os.path.join(self.tempdir, "invalid.xml")

    def get_nonexistant_file_path(self):
        return os.path.join(self.tempdir, "strings.xml")

    def get_nonexistant_file_resource(self, path):
        contents = dedent(
            """<?xml version="1.0" encoding="utf-8"?>
            <resources>
                <string name="source-string">Source String</string>
            </resources>
        """
        )

        source_path = create_named_tempfile(
            contents,
            prefix="strings",
            suffix=".xml",
            directory=self.tempdir,
        )
        source_resource = xml.XMLResource(source_path)

        return xml.XMLResource(
            path,
            source_resource=source_resource,
        )

    def test_init_invalid_resource(self):
        """
        If no parser cannot be found for the translated resource,
        raise a ParseError.
        """
        path = self.get_invalid_file_path()
        with pytest.raises(ParseError):
            xml.XMLResource(path, source_resource=None)

    def test_init_missing_resource(self):
        """
        If the translated resource doesn't exist and no source resource is
        given, raise a ParseError.
        """
        path = self.get_nonexistant_file_path()
        with pytest.raises(ParseError):
            xml.XMLResource(path, source_resource=None)

    def test_init_missing_resource_with_source(self):
        """
        If the translated resource doesn't exist but a source resource is
        given, return a resource with empty translations.
        """
        path = self.get_nonexistant_file_path()
        translated_resource = self.get_nonexistant_file_resource(path)

        assert len(translated_resource.entities) == 1
        assert next(iter(translated_resource.entities.values())).strings == {}


BASE_ANDROID_XML_FILE = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Sample comment -->
    <string name="Source String">Translated String</string>

    <!-- First comment -->
    <!-- Second comment -->
    <string name="Multiple Comments">Translated Multiple Comments</string>

    <string name="No Comments or Sources">Translated No Comments or Sources</string>
    <string name="Empty Translation"></string>
</resources>
"""


class AndroidXMLTests(FormatTestsMixin, TestCase):
    parse = staticmethod(xml.parse)
    supports_keys = False
    supports_source = False
    supports_source_string = False

    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tempdir)

    def parse_string(
        self,
        string,
        source_string=None,
        locale=None,
        path=None,
        source_path=None,
    ):
        """Android XML files must contain the word 'strings'."""
        path = create_named_tempfile(
            string,
            prefix="strings",
            suffix=".xml",
            directory=self.tempdir,
        )
        if source_string is not None:
            source_path = create_named_tempfile(
                source_string,
                prefix="strings",
                suffix=".xml",
                directory=self.tempdir,
            )
        return super().parse_string(
            string,
            source_string=source_string,
            locale=locale,
            path=path,
            source_path=source_path,
        )

    def test_parse_basic(self):
        self.run_parse_basic(BASE_ANDROID_XML_FILE, 0)

    def test_parse_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_ANDROID_XML_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_ANDROID_XML_FILE, 2)

    def test_parse_empty_translation(self):
        self.run_parse_empty_translation(BASE_ANDROID_XML_FILE, 3)

    def test_quotes(self):
        tempdir = tempfile.mkdtemp()

        path = create_named_tempfile(
            dedent(
                """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="String">\'</string>
</resources>
        """
            ),
            prefix="strings",
            suffix=".xml",
            directory=tempdir,
        )

        translations = self.parse(path)

        # Unescape quotes when parsing
        assert_attributes_equal(translations[0], strings={None: "'"})
