from __future__ import absolute_import

from mock import patch, PropertyMock

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
            "pontoon.sync.changeset.ChangeSet.changed_translations",
            new_callable=PropertyMock,
        )

        self.mock_changed_translations = changed_translation_patch.start()
        self.addCleanup(changed_translation_patch.stop)

    def test_bulk_check_translations_no_translations(self):
        self.mock_changed_translations.return_value = []

        assert self.changeset.bulk_check_translations() == set()
        assert not Error.objects.exists()
        assert not Warning.objects.exists()

    def test_bulk_check_valid_translations(self):
        translation1, translation2 = TranslationFactory.create_batch(
            2,
            locale=self.translated_locale,
            entity=self.main_db_entity,
            approved=True,
            date=aware_datetime(2015, 1, 1),
        )

        self.mock_changed_translations.return_value = [
            translation1,
            translation2,
        ]
        assert self.changeset.bulk_check_translations() == {
            translation1.pk,
            translation2.pk,
        }
        assert not Error.objects.exists()
        assert not Warning.objects.exists()

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
            date=aware_datetime(2015, 1, 1),
        )
        invalid_translation.string = "a\nb"
        invalid_translation.save()

        # Clear TM entries for those translations
        invalid_translation.memory_entries.all().delete()
        valid_translation.memory_entries.all().delete()

        self.mock_changed_translations.return_value = [
            invalid_translation,
            valid_translation,
        ]

        valid_translations = self.changeset.bulk_check_translations()

        assert valid_translations == {valid_translation.pk}

        (error,) = Error.objects.all()

        assert error.library == "p"
        assert error.message == "Newline characters are not allowed"
        assert error.translation == invalid_translation

        self.changeset.translations_to_update = {
            valid_translation.pk: valid_translation
        }

        self.changeset.bulk_create_translation_memory_entries(valid_translations)

        assert not invalid_translation.memory_entries.exists()
        assert valid_translation.memory_entries.count() == 1
