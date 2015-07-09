from datetime import datetime

import mock
import polib
from django_nose.tools import assert_equal

from pontoon.administration.files import dump_po
from pontoon.base.tests import (
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TestCase,
    TranslationFactory,
)


class DumpPOTests(TestCase):
    def setUp(self):
        """
        Set up a fake locale, project, and pofile for dump_po to modify.
        """
        self.locale = LocaleFactory.create(code='fake')
        self.project = ProjectFactory.create(
            slug='valid-project',
            locales=[self.locale],
            last_committed=datetime(2015, 2, 1)
        )
        self.resource = ResourceFactory.create(
            path='foo/bar.po',
            project=self.project
        )

        self.fake_pofile = polib.pofile("""
            msgid "Id1"
            msgstr "Str1"

            msgid "Id2"
            msgstr "Str2"
        """)
        self.fake_pofile.save = mock.Mock()

        self.patches = {
            'pofile': mock.patch(
                'pontoon.administration.files.polib.pofile',
                return_value=self.fake_pofile
            ),
            'get_locale_directory': mock.patch(
                'pontoon.administration.files.get_locale_directory',
                return_value={'name': 'test', 'path': '/test'}
            ),
        }

        super(DumpPOTests, self).setUp()

    def create_translation(self, key, string, approved=True, approved_date=None):
        TranslationFactory.create(
            string=string,
            entity__string=key,
            approved=approved,
            approved_date=approved_date or datetime(2015, 3, 1),
            entity__resource=self.resource,
            locale=self.locale
        )

    def assert_translated(self, key, expected_string):
        assert_equal(self.fake_pofile.find(key).msgstr, expected_string)

    def test_update_approved_translations(self):
        """Ensure that only approved translations are updated."""
        # Id1 translation unapproved.
        self.create_translation('Id1', 'NewStr', approved=False)

        # Id2 translation approved.
        self.create_translation('Id2', 'NewStr', approved=True)

        dump_po(self.project, self.locale, 'foo/bar.po')
        self.assert_translated('Id1', 'Str1')
        self.assert_translated('Id2', 'NewStr')

    def test_only_update_new_translations(self):
        """
        Ensure that only entities that have translations newer than the
        last update are modified.
        """
        # Id1 translation approved before last dump.
        self.create_translation('Id1', 'NewStr', approved_date=datetime(2015, 1, 1))

        # Id2 translation approved after last dump.
        self.create_translation('Id2', 'NewStr', approved_date=datetime(2015, 3, 1))

        dump_po(self.project, self.locale, 'foo/bar.po')
        self.assert_translated('Id1', 'Str1')
        self.assert_translated('Id2', 'NewStr')
