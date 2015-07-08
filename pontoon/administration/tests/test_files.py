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
            last_dumped=datetime(2015, 2, 1)
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

        patches = [
            mock.patch('pontoon.administration.files.polib.pofile',
                       return_value=self.fake_pofile),
            mock.patch('pontoon.administration.files.get_locale_directory',
                       return_value={'name': 'test', 'path': '/test'}),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def test_only_update_new_translations(self):
        """
        Ensure that only entities that have translations newer than the
        last update are modified.
        """
        # Id1 translation approved before last dump.
        TranslationFactory.create(string='Id1', entity__string='NewStr',
                                  approved=True, approved_date=datetime(2015, 1, 1),
                                  entity__resource=self.resource, locale=self.locale)

        # Id2 translation approved after last dump.
        TranslationFactory.create(string='Id2', entity__string='NewStr',
                                  approved=True, approved_date=datetime(2015, 3, 1),
                                  entity__resource=self.resource, locale=self.locale)

        dump_po(self.project, self.locale, 'foo/bar.po')
        assert_equal(self.fake_pofile.find('Id1').msgstr, 'Str1')
        assert_equal(self.fake_pofile.find('Id2').msgstr, 'NewStr')
