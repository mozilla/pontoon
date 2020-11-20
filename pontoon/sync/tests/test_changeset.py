from unittest.mock import Mock, MagicMock, patch

import pytest

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Entity
from pontoon.base.tests import (
    assert_attributes_equal,
    TranslationFactory,
    UserFactory,
)
from pontoon.base.utils import aware_datetime
from pontoon.sync.tests import FakeCheckoutTestCase


class ChangeSetTests(FakeCheckoutTestCase):
    def test_execute_called_once(self):
        """Raise a RuntimeError if execute is called more than once."""
        self.changeset.execute()
        with pytest.raises(RuntimeError):
            self.changeset.execute()

    def update_main_vcs_entity(self, **translation_changes):
        for key, value in translation_changes.items():
            setattr(self.main_db_translation, key, value)
        self.main_db_translation.save()

        self.changeset.update_vcs_entity(
            self.translated_locale, self.main_db_entity, self.main_vcs_entity
        )
        self.changeset.execute()

    def test_changed_translations_created(self):
        """
        Return a list of Translation objects that have been created.
        """
        self.main_db_translation.delete()
        self.update_main_db_entity()
        translation = self.main_db_entity.translation_set.all()[0]
        assert self.changeset.changed_translations == [translation]

    def test_changed_translations_no_changes(self):
        """
        If there are no changes, changed_translations should return empty list.
        """
        assert self.changeset.changed_translations == []

    def test_update_vcs_entity(self):
        """
        Update the VCS translations with translations in the database.
        """
        self.main_vcs_resource.save = Mock()
        self.other_vcs_resource.save = Mock()

        self.update_main_vcs_entity(string="New Translated String")
        assert self.main_vcs_translation.strings == {None: "New Translated String"}

        # Ensure only resources that were updated are saved.
        assert self.main_vcs_resource.save.called
        assert not self.other_vcs_resource.save.called

        # Update the VCS translation with info about the last
        # translation.
        assert self.main_vcs_translation.last_updated == self.main_db_translation.date
        assert (
            self.main_vcs_translation.last_translator == self.main_db_translation.user
        )

    def test_update_vcs_entity_unapproved(self):
        """
        Do not update VCS with unapproved translations. If no approved
        translations exist, delete existing ones.
        """
        self.update_main_vcs_entity(approved=False)
        assert self.main_vcs_translation.strings == {}

    def test_update_vcs_entity_fuzzy(self):
        self.main_vcs_translation.fuzzy = False
        self.update_main_vcs_entity(fuzzy=True)
        assert self.main_vcs_translation.fuzzy

    def test_update_vcs_entity_not_fuzzy(self):
        self.main_vcs_translation.fuzzy = True
        self.update_main_vcs_entity(fuzzy=False)
        assert not self.main_vcs_translation.fuzzy

    def test_update_vcs_last_translation_no_translations(self):
        """
        If there are no translations in the database, do not set the
        last_updated and last_translator fields on the VCS translation.
        """
        self.main_db_translation.delete()

        self.changeset.update_vcs_entity(
            self.translated_locale, self.main_db_entity, self.main_vcs_entity
        )
        self.changeset.execute()

        assert self.main_vcs_translation.last_updated is None
        assert self.main_vcs_translation.last_translator is None

    def test_update_vcs_entity_user(self):
        """Track translation authors for use in the commit message."""
        user = UserFactory.create()
        self.update_main_vcs_entity(user=user)
        assert self.changeset.commit_authors_per_locale["translated-locale"] == [user]

    def test_create_db(self):
        """Create new entity in the database."""
        self.main_db_entity.delete()

        self.main_vcs_entity.key = "Source String"
        self.main_vcs_entity.comments = ["first comment", "second"]
        self.main_vcs_entity.order = 7
        self.main_vcs_translation.fuzzy = False
        self.main_vcs_entity.string_plural = "plural string"
        self.main_vcs_entity.source = ["foo.py:87"]

        self.changeset.create_db_entity(self.main_vcs_entity)
        self.changeset.execute()
        new_entity = Entity.objects.get(
            resource__path=self.main_vcs_resource.path,
            string=self.main_vcs_entity.string,
        )
        assert_attributes_equal(
            new_entity,
            resource=self.main_db_resource,
            string="Source String",
            key="Source String",
            comment="first comment\nsecond",
            order=7,
            string_plural="plural string",
            source=["foo.py:87"],
        )

        new_translation = new_entity.translation_set.all()[0]
        assert_attributes_equal(
            new_translation,
            locale=self.translated_locale,
            string="Translated String",
            plural_form=None,
            approved=True,
            approved_date=aware_datetime(1970, 1, 1),
            fuzzy=False,
        )

    def update_main_db_entity(self):
        self.changeset.update_db_entity(
            self.translated_locale, self.main_db_entity, self.main_vcs_entity
        )
        self.changeset.execute()

    def test_update_db_existing_translation(self):
        """
        Update an existing translation in the DB with changes from VCS.
        """
        # Set up DB and VCS to differ and require an update.
        self.main_db_translation.fuzzy = True
        self.main_db_translation.extra = {}
        self.main_db_translation.save()

        self.main_vcs_entity.key = "Source String"
        self.main_vcs_entity.comments = ["first comment", "second"]
        self.main_vcs_entity.order = 7
        self.main_vcs_entity.string_plural = "plural string"
        self.main_vcs_entity.source = ["foo.py:87"]
        self.main_vcs_translation.fuzzy = False
        # The test translation is from a langfile so we can use tags
        # for testing extra.
        self.main_vcs_translation.tags = set(["ok"])

        self.update_main_db_entity()
        self.main_db_entity.refresh_from_db()
        assert_attributes_equal(
            self.main_db_entity,
            key="Source String",
            comment="first comment\nsecond",
            order=7,
            string_plural="plural string",
            source=["foo.py:87"],
        )

        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation, fuzzy=False, extra={"tags": ["ok"]}
        )

    def test_update_db_clean_entity_translation(self):
        """
        If no changes have been made to the database entity or the
        translation, do not bother updating them in the database.
        """
        self.update_main_db_entity()

        # TODO: It'd be nice if we didn't rely on internal changeset
        # attributes to check this, but not vital.
        assert self.main_db_entity not in self.changeset.entities_to_update
        assert self.main_db_translation not in self.changeset.translations_to_update

    def test_update_db_approve_translation(self):
        """
        Approve any un-approved translations that have counterparts in
        VCS.
        """
        self.main_db_translation.approved = False
        self.main_db_translation.approved_date = None
        self.main_db_translation.save()

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation,
            approved=True,
            approved_date=aware_datetime(1970, 1, 1),
        )

        assert ActionLog.objects.filter(
            action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
            translation=self.main_db_translation.pk,
        ).exists()

    def test_update_db_dont_approve_fuzzy(self):
        """
        Do not approve un-approved translations that have non-fuzzy
        counterparts in VCS.
        """
        self.main_db_translation.approved = False
        self.main_db_translation.approved_date = None
        self.main_db_translation.save()
        self.main_vcs_translation.fuzzy = True

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation, approved=False, approved_date=None
        )

    def test_update_db_new_translation(self):
        """
        If a matching translation does not exist in the database, create a new
        one.
        """
        self.main_db_translation.delete()
        self.update_main_db_entity()

        translation = self.main_db_entity.translation_set.all()[0]
        assert_attributes_equal(
            translation,
            locale=self.translated_locale,
            string="Translated String",
            plural_form=None,
            approved=True,
            approved_date=aware_datetime(1970, 1, 1),
            fuzzy=False,
            extra={"tags": []},
        )

        assert ActionLog.objects.filter(
            action_type=ActionLog.ActionType.TRANSLATION_CREATED,
            translation=translation.pk,
        ).exists()

    def test_update_db_unfuzzy_existing(self):
        """
        Any existing fuzzy translations get unfuzzied.
        """
        self.main_db_translation.approved = False
        self.main_db_translation.fuzzy = True
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = "New Translated String"

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(self.main_db_translation, fuzzy=False)

    def test_update_db_unapprove_existing(self):
        """
        Any existing translations that don't match anything in VCS get
        unapproved, unless they were created after self.now.
        """
        self.main_db_translation.approved = True
        self.main_db_translation.approved_date = aware_datetime(1970, 1, 1)
        self.main_db_translation.approved_user = UserFactory.create()
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = "New Translated String"

        created_after_translation = TranslationFactory.create(
            entity=self.main_db_entity,
            approved=True,
            approved_date=aware_datetime(1970, 1, 3),
        )

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation,
            approved=False,
            approved_user=None,
            approved_date=None,
        )

        assert ActionLog.objects.filter(
            action_type=ActionLog.ActionType.TRANSLATION_REJECTED,
            translation=self.main_db_translation.pk,
        ).exists()

        created_after_translation.refresh_from_db()
        assert_attributes_equal(
            created_after_translation,
            approved=True,
            approved_date=aware_datetime(1970, 1, 3),
        )

    def test_update_db_unapprove_fuzzy(self):
        """
        If an existing translation is fuzzy and doesn't match anything in VCS,
        unapprove and unfuzzy that translation without rejecting it.
        """
        self.main_db_translation.fuzzy = True
        self.main_db_translation.approved = True
        self.main_db_translation.approved_date = aware_datetime(1970, 1, 1)
        self.main_db_translation.approved_user = UserFactory.create()
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = "New Translated String"

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation,
            approved=False,
            approved_user=None,
            approved_date=None,
            rejected=False,
            fuzzy=False,
        )

        assert ActionLog.objects.filter(
            action_type=ActionLog.ActionType.TRANSLATION_UNAPPROVED,
            translation=self.main_db_translation.pk,
        ).exists()

    def test_update_db_unapprove_clean(self):
        """
        If translations that are set to be unapproved were already unapproved,
        don't bother updating them.
        """
        self.main_db_translation.approved = False
        self.main_db_translation.approved_date = None
        self.main_db_translation.approved_user = None
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = "New Translated String"

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert self.main_db_translation not in self.changeset.translations_to_update

    def test_update_db_reject_approved(self):
        """
        When a translation is submitted through VCS, reject any existing approved translations.
        """
        self.main_db_translation.approved = True
        self.main_db_translation.approved_date = aware_datetime(1970, 1, 1)
        self.main_db_translation.approved_user = UserFactory.create()
        self.main_db_translation.rejected = False
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = "New Translated String"

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation, rejected=True,
        )

        assert ActionLog.objects.filter(
            action_type=ActionLog.ActionType.TRANSLATION_REJECTED,
            translation=self.main_db_translation.pk,
        ).exists()

    def test_update_db_reject_approved_skip_fuzzy(self):
        """
        When a translation is submitted through VCS, reject any existing approved translations.
        Unless the same translation is submitted and only made fuzzy.
        """
        self.main_db_translation.approved = True
        self.main_db_translation.approved_date = aware_datetime(1970, 1, 1)
        self.main_db_translation.approved_user = UserFactory.create()
        self.main_db_translation.rejected = False
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = self.main_db_translation.string
        self.main_vcs_translation.fuzzy = True

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation, rejected=False,
        )

    def test_obsolete_db(self):
        self.changeset.obsolete_db_entity(self.main_db_entity)
        self.changeset.execute()
        self.main_db_entity.refresh_from_db()
        assert self.main_db_entity.obsolete

    def test_no_new_translations(self):
        """
        Don't change any resource if there aren't any new translations.
        """
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            approved=True,
            date=aware_datetime(2015, 1, 1),
        )

        with patch.object(
            self.main_db_entity, "has_changed", return_value=False
        ) as mock_has_changed:
            resource_file = MagicMock()
            self.changeset.update_vcs_entity(
                self.translated_locale, self.main_db_entity, MagicMock()
            )
            self.changeset.vcs_project.resources = {
                self.main_db_entity.resource.path: resource_file
            }

            self.changeset.execute_update_vcs()

            assert mock_has_changed.called
            assert not resource_file.save.called

    def test_changed_resources_sync(self):
        """
        Synchronization should modify resource files if there
        are changed translations.
        """
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            approved=True,
            date=aware_datetime(2015, 1, 1),
        )

        resource_file = MagicMock()
        self.changeset.vcs_project.resources = {
            self.main_db_entity.resource.path: resource_file
        }

        with patch.object(
            self.main_db_entity, "has_changed", return_value=True
        ) as mock_has_changed:
            self.changeset.update_vcs_entity(
                self.translated_locale, self.main_db_entity, MagicMock()
            )

            self.changeset.execute_update_vcs()
            assert mock_has_changed.called
            assert resource_file.save.called

    def test_unchanged_resources_sync(self):
        """
        Synchronization shouldn't modify resources if their
        entities weren't changed.
        """
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            approved=True,
            date=aware_datetime(2015, 1, 1),
        )

        resource_file = MagicMock()
        self.changeset.vcs_project.resources = {
            self.main_db_entity.resource.path: resource_file
        }

        with patch.object(
            self.main_db_entity, "has_changed", return_value=False
        ) as mock_has_changed:
            self.changeset.update_vcs_entity(
                self.translated_locale, self.main_db_entity, MagicMock()
            )

            self.changeset.execute_update_vcs()
            assert mock_has_changed.called
            assert len(resource_file.save.mock_calls) == 0


class AuthorsTests(FakeCheckoutTestCase):
    """
    Tests authors of translations passed to the final commit message.
    """

    def test_multiple_authors(self):
        """
        Commit message should include authors from translations of separate
        entities.
        """
        first_author, second_author = UserFactory.create_batch(2)
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            user=first_author,
            approved=True,
        )
        TranslationFactory.create(
            locale=self.translated_locale, entity=self.main_db_entity, approved=False
        )
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.other_db_entity,
            user=second_author,
            approved=True,
        )
        TranslationFactory.create(
            locale=self.translated_locale, entity=self.other_db_entity, approved=False
        )

        self.changeset.update_vcs_entity(
            self.translated_locale, self.main_db_entity, MagicMock()
        )
        self.changeset.update_vcs_entity(
            self.translated_locale, self.other_db_entity, MagicMock()
        )

        self.changeset.execute_update_vcs()

        assert self.changeset.commit_authors_per_locale[
            self.translated_locale.code
        ] == [first_author, second_author]

    def test_plural_translations(self):
        """
        If entity has some plural translations and approved translations their authors
        should be included in commit message.
        """
        first_author, second_author, third_author = UserFactory.create_batch(3)

        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            user=first_author,
            approved=True,
        )
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            user=third_author,
            approved=True,
            plural_form=1,
        )
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            user=second_author,
            approved=False,
        )

        self.changeset.update_vcs_entity(
            self.translated_locale, self.main_db_entity, MagicMock()
        )

        self.changeset.execute_update_vcs()

        assert set(
            self.changeset.commit_authors_per_locale[self.translated_locale.code]
        ) == {first_author, third_author}

    def test_multiple_translations(self):
        """
        If there are multiple translations to the same locale, only authors of
        the final approved version should be returned.
        """
        first_author, second_author = UserFactory.create_batch(2)

        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            user=first_author,
            approved=True,
        )
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            user=second_author,
            approved=False,
        )

        self.changeset.update_vcs_entity(
            self.translated_locale, self.main_db_entity, MagicMock()
        )

        self.changeset.execute_update_vcs()

        assert self.changeset.commit_authors_per_locale[
            self.translated_locale.code
        ] == [first_author]

    def test_no_translations(self):
        """
        We don't attribute anyone if there aren't any new translations.
        """
        TranslationFactory.create(
            locale=self.translated_locale,
            entity=self.main_db_entity,
            approved=True,
            date=aware_datetime(2015, 1, 1),
        )

        with patch.object(self.main_db_entity, "has_changed", return_value=False):
            self.changeset.update_vcs_entity(
                self.translated_locale, self.main_db_entity, MagicMock()
            )
            self.changeset.execute_update_vcs()
            assert (
                self.changeset.commit_authors_per_locale[self.translated_locale.code]
                == []
            )
