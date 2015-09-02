import os.path

from django_nose.tools import assert_equal

from pontoon.base.formats import lang
from pontoon.base.tests import assert_attributes_equal, TestCase


class LangTests(TestCase):
    def test_load_utf8_bom(self):
        """
        Ensure that the langfile parser can load UTF-8 files with an encoded
        BOM at the beginning of the file.

        See https://docs.python.org/2/library/codecs.html for details (search
        for the string "utf-8-sig").
        """
        current_dir = os.path.dirname(__file__)
        resource = lang.parse(os.path.join(current_dir, 'bom.lang'))
        assert_equal(len(resource.translations), 1)
        assert_attributes_equal(
            resource.translations[0],
            source_string='Source String',
            strings={None: 'Translated String'}
        )
