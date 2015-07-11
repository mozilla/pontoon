from datetime import datetime
from StringIO import StringIO

import mock
import polib
from django_nose.tools import assert_equal
from translate.storage import xliff

from pontoon.administration.files import dump_po, dump_xliff
from pontoon.base.tests import (
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TestCase,
    TranslationFactory,
)


class DumpResourceTests(TestCase):
    resource_path = 'fake.file'

    def setUp(self):
        super(DumpResourceTests, self).setUp()

        self.locale = LocaleFactory.create(code='fake')
        self.project = ProjectFactory.create(
            slug='valid-project',
            locales=[self.locale],
            last_committed=datetime(2015, 2, 1)
        )
        self.resource = ResourceFactory.create(
            path=self.resource_path,
            project=self.project
        )

        # Mock open and get_locale_directory to avoid errors about
        # invalid paths.
        self.open = self.register_patch(mock.patch(
            'pontoon.administration.files.open', mock.mock_open(), create=True))
        self.get_locale_directory = self.register_patch(mock.patch(
            'pontoon.administration.files.get_locale_directory',
            return_value={'name': 'test', 'path': '/test'}
        ))

    def create_translation(self, key, string, approved=True, approved_date=None):
        TranslationFactory.create(
            string=string,
            entity__key=key,
            entity__string=key,
            approved=approved,
            approved_date=approved_date or datetime(2015, 3, 1),
            entity__resource=self.resource,
            locale=self.locale
        )


class DumpTestsMixin(object):
    """
    Mixin that contains tests that are common to all dump_* functions.

    These are kept separate from DumpResourceTests so that they're not
    run except on subclasses.
    """

    # Subclasses should set this to the dump_* function they want to
    # test, usually wrapped in a staticmethod() call.
    dump_functions = None

    def assert_translated(self, key, expected_string):
        """
        Assert that the entity witht he given key was dumped with the
        given string as its translation.

        This is highly dependent on how the subclass mocks the dump_*
        function.
        """
        raise NotImplementedError()

    def test_update_approved_translations(self):
        """Ensure that only approved translations are updated."""
        # Id1 translation unapproved.
        self.create_translation('Id1', 'NewStr', approved=False)

        # Id2 translation approved.
        self.create_translation('Id2', 'NewStr', approved=True)

        self.dump_function(self.project, self.locale, self.resource_path)
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

        self.dump_function(self.project, self.locale, self.resource_path)
        self.assert_translated('Id1', 'Str1')
        self.assert_translated('Id2', 'NewStr')


class DumpPOTests(DumpResourceTests, DumpTestsMixin):
    dump_function = staticmethod(dump_po)
    resource_path = 'foo/bar.po'

    def setUp(self):
        """Set up a fake pofile for dump_po to modify."""
        super(DumpPOTests, self).setUp()

        self.fake_pofile = polib.pofile("""
            msgid "Id1"
            msgstr "Str1"

            msgid "Id2"
            msgstr "Str2"
        """)
        self.fake_pofile.save = mock.Mock()

        self.register_patch(mock.patch(
            'pontoon.administration.files.polib.pofile',
            return_value=self.fake_pofile
        ))

    def assert_translated(self, key, expected_string):
        assert_equal(self.fake_pofile.find(key).msgstr, expected_string)


class DumpXLIFFTests(DumpResourceTests, DumpTestsMixin):
    dump_function = staticmethod(dump_xliff)
    resource_path = 'foo/bar.xliff'

    def setUp(self):
        super(DumpXLIFFTests, self).setUp()

        self.fake_xlifffile = xliff.xlifffile(StringIO("""
            <xliff version="1.2">
              <file>
                <body>
                  <trans-unit id="Id1">
                    <source>Str1</source>
                    <target>Str1</target>
                  </trans-unit>
                  <trans-unit id="Id2">
                    <source>Str2</source>
                    <target>Str2</target>
                  </trans-unit>
                </body>
              </file>
            </xliff>
        """))

        self.xliff = self.register_patch(mock.patch(
            'pontoon.administration.files.xliff'))
        self.xliff.xlifffile.return_value = self.fake_xlifffile

    def assert_translated(self, key, expected_string):
        try:
            unit = next(unit for unit in self.fake_xlifffile.units
                        if unit.getid() == key)
        except StopIteration:
            raise AssertionError('No unit found with key "{0}"'.format(key))

        assert_equal(unit.gettarget(), expected_string)
