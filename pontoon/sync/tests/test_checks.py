from mock import patch, PropertyMock

from django_nose.tools import assert_equal

from pontoon.base.utils import aware_datetime
from pontoon.base.tests import TranslationFactory
from pontoon.checks.models import (
    Warning,
    Error,
)
from pontoon.sync.tests import FakeCheckoutTestCase


class TestChangesetTranslationsChecks(FakeCheckoutTestCase):
    """
    Semi-integration tests for translation checks during a sync.
    """
    def setUp(self):
        super(TestChangesetTranslationsChecks, self).setUp()

        changed_translation_patch = patch(
            'pontoon.sync.changeset.ChangeSet.changed_translations',
            new_callable=PropertyMock
        )

        self.mock_changed_translations = changed_translation_patch.start()
        self.addCleanup(changed_translation_patch.stop)

    def test_bulk_check_translations_no_translations(self):
        self.mock_changed_translations.return_value = []

        assert_equal(self.changeset.bulk_check_translations(), set())
        assert_equal(Error.objects.count(), 0)
        assert_equal(Warning.objects.count(), 0)

    def test_bulk_check_valid_translations(self):
        translation1, translation2 = TranslationFactory.create_batch(
            2,
            locale=self.translated_locale,
            entity=self.main_db_entity,
            approved=True,
            date=aware_datetime(2015, 1, 1)
        )

        self.mock_changed_translations.return_value = [
            translation1,
            translation2,
        ]
        assert_equal(
            self.changeset.bulk_check_translations(),
            {
                translation1.pk,
                translation2.pk,
            }
        )
        assert_equal(Error.objects.count(), 0)
        assert_equal(Warning.objects.count(), 0)

    def test_bulk_check_invalid_translations(self):
        """
        Test scenario:
        * check if errors are detected
        * check if only valid translation will land in the Translate Memory
        """
        invalid_translation, valid_translation = TranslationFactory.create_batch(
            2,
            locale=self.translated_locale,
            entity=self.main_db_entity,
            approved=True,
            date=aware_datetime(2015, 1, 1)
        )
        invalid_translation.string = 'a\nb'
        invalid_translation.save()

        # Clear TM entries for those translations
        invalid_translation.memory_entries.all().delete()
        valid_translation.memory_entries.all().delete()

        self.mock_changed_translations.return_value = [
            invalid_translation,
            valid_translation,
        ]

        valid_translations = self.changeset.bulk_check_translations()

        assert_equal(valid_translations, {valid_translation.pk})

        error, = Error.objects.all()

        assert_equal(error.library, 'p')
        assert_equal(error.message, 'Newline characters are not allowed')
        assert_equal(error.translation, invalid_translation)

        self.changeset.translations_to_update = {
            valid_translation.pk: valid_translation
        }

        self.changeset.bulk_create_translation_memory_entries(valid_translations)

        assert_equal(invalid_translation.memory_entries.count(), 0)
        assert_equal(valid_translation.memory_entries.count(), 1)
