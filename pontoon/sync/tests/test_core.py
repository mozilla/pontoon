import os.path
from unittest.mock import ANY, Mock, patch, PropertyMock, MagicMock

import pytest

from pontoon.base.models import (
    Entity,
    Repository,
    Resource,
    TranslatedResource,
)
from pontoon.base.tests import (
    CONTAINS,
    NOT,
    UserFactory,
)
from pontoon.sync.core import (
    commit_changes,
    entity_key,
    pull_locale_repo_changes,
    update_entities,
    update_resources,
    update_translated_resources,
    update_translated_resources_with_config,
    update_translated_resources_without_config,
    update_translations,
)
from pontoon.sync.tests import FAKE_CHECKOUT_PATH, FakeCheckoutTestCase


class UpdateEntityTests(FakeCheckoutTestCase):
    def call_update_entities(self, collected):
        with patch("pontoon.sync.core.collect_entities") as mock_collect_entities:
            mock_collect_entities.return_value = collected
            return update_entities(self.db_project, self.vcs_project, self.changeset)

    def test_none(self):
        """
        If both the db_entity and vcs_entity are None, raise a
        CommandError, as that should never happen.
        """
        with pytest.raises(ValueError):
            self.call_update_entities([("key", None, None)])

    def test_obsolete(self):
        """If VCS is missing the entity in question, obsolete it."""
        self.changeset.obsolete_db_entity = Mock()
        self.call_update_entities([("key", self.main_db_entity, None)])
        self.changeset.obsolete_db_entity.assert_called_with(self.main_db_entity)

    def test_create(self):
        """If the DB is missing an entity in VCS, create it."""
        self.changeset.create_db_entity = Mock()
        self.call_update_entities([("key", None, self.main_vcs_entity)])
        self.changeset.create_db_entity.assert_called_with(self.main_vcs_entity)


class UpdateTranslationsTests(FakeCheckoutTestCase):
    def call_update_translations(self, collected):
        with patch("pontoon.sync.core.collect_entities") as mock_collect_entities:
            mock_collect_entities.return_value = collected
            return update_translations(
                self.db_project,
                self.vcs_project,
                self.translated_locale,
                self.changeset,
            )

    def test_missing_entities(self):
        """If either of the entities is missing, skip it."""
        self.changeset.update_vcs_entity = Mock()
        self.changeset.update_db_entity = Mock()

        self.call_update_translations(
            [
                ("one", None, self.main_vcs_entity),
                ("other", self.main_db_entity, None),
                ("both", None, None),
            ]
        )
        assert not self.changeset.update_vcs_entity.called
        assert not self.changeset.update_db_entity.called

    def test_no_translation(self):
        """If no translation exists for a specific locale, skip it."""
        self.changeset.update_vcs_entity = Mock()
        self.changeset.update_db_entity = Mock()
        self.main_vcs_entity.has_translation_for = Mock(return_value=False)

        self.call_update_translations(
            [("key", self.main_db_entity, self.main_vcs_entity)]
        )
        assert not self.changeset.update_vcs_entity.called
        assert not self.changeset.update_db_entity.called

    def test_db_changed(self):
        """
        If the DB entity has changed since the last sync, update the
        VCS.
        """
        self.changeset.update_vcs_entity = Mock()
        with patch.object(Entity, "has_changed", return_value=True):
            self.call_update_translations(
                [("key", self.main_db_entity, self.main_vcs_entity)]
            )

        self.changeset.update_vcs_entity.assert_called_with(
            self.translated_locale, self.main_db_entity, self.main_vcs_entity
        )

    def test_vcs_changed(self):
        """
        If the DB entity has not changed since the last sync, update the DB with
        the latest changes from VCS.
        """
        self.changeset.update_db_entity = Mock()
        with patch.object(Entity, "has_changed", return_value=False):
            self.call_update_translations(
                [("key", self.main_db_entity, self.main_vcs_entity)]
            )

        self.changeset.update_db_entity.assert_called_with(
            self.translated_locale, self.main_db_entity, self.main_vcs_entity
        )


class UpdateResourcesTests(FakeCheckoutTestCase):
    def test_basic(self):
        # Check for self.main_db_resource to be updated and
        # self.other_db_resource to be created.
        self.main_db_resource.total_strings = 5000
        self.main_db_resource.save()
        self.other_db_resource.delete()

        update_resources(self.db_project, self.vcs_project)
        self.main_db_resource.refresh_from_db()
        assert self.main_db_resource.total_strings == len(
            self.main_vcs_resource.entities
        )

        other_db_resource = Resource.objects.get(path=self.other_vcs_resource.path)
        assert other_db_resource.total_strings == len(self.other_vcs_resource.entities)


class UpdateTranslatedResourcesTests(FakeCheckoutTestCase):
    @patch("pontoon.sync.core.update_translated_resources_without_config")
    @patch("pontoon.sync.core.update_translated_resources_with_config")
    def test_with_or_without_project_config(
        self,
        update_translated_resources_with_config_mock,
        update_translated_resources_without_config_mock,
    ):
        """
        Pick the right update_translated_resources() method, depending on
        whether the project configuration file is provided or not.
        """
        # Without project config
        self.vcs_project.configuration = None
        update_translated_resources(
            self.db_project, self.vcs_project, self.translated_locale,
        )
        assert not update_translated_resources_with_config_mock.called
        assert update_translated_resources_without_config_mock.called

        # Reset called value
        update_translated_resources_with_config_mock.called = False
        update_translated_resources_without_config_mock.called = False

        # With project config
        self.vcs_project.configuration = True
        update_translated_resources(
            self.db_project, self.vcs_project, self.translated_locale,
        )
        assert update_translated_resources_with_config_mock.called
        assert not update_translated_resources_without_config_mock.called

    def test_project_configuration_basic(self):
        """
        Create/update the TranslatedResource objects based on project configuration.
        """
        with patch.object(self.vcs_project, "configuration") as configuration:
            with patch.object(configuration, "locale_resources") as locale_resources:
                locale_resources.return_value = [
                    self.other_db_resource,
                ]

                update_translated_resources_with_config(
                    self.db_project, self.vcs_project, self.translated_locale,
                )

                assert TranslatedResource.objects.filter(
                    resource=self.other_db_resource, locale=self.translated_locale,
                ).exists()

                assert not TranslatedResource.objects.filter(
                    resource=self.missing_db_resource, locale=self.translated_locale,
                ).exists()

    def test_no_project_configuration_basic(self):
        """
        Create/update the TranslatedResource object on all resources
        available in the current locale.
        """
        update_translated_resources_without_config(
            self.db_project, self.vcs_project, self.translated_locale,
        )

        assert TranslatedResource.objects.filter(
            resource=self.main_db_resource, locale=self.translated_locale
        ).exists()

        assert TranslatedResource.objects.filter(
            resource=self.other_db_resource, locale=self.translated_locale
        ).exists()

        assert not TranslatedResource.objects.filter(
            resource=self.missing_db_resource, locale=self.translated_locale
        ).exists()

    def test_no_project_configuration_asymmetric(self):
        """
        Create/update the TranslatedResource object on asymmetric resources
        even if they don't exist in the target locale.
        """
        with patch.object(
            Resource, "is_asymmetric", new_callable=PropertyMock
        ) as is_asymmetric:
            is_asymmetric.return_value = True

            update_translated_resources_without_config(
                self.db_project, self.vcs_project, self.translated_locale,
            )

            assert TranslatedResource.objects.filter(
                resource=self.main_db_resource, locale=self.translated_locale
            ).exists()

            assert TranslatedResource.objects.filter(
                resource=self.other_db_resource, locale=self.translated_locale
            ).exists()

            assert TranslatedResource.objects.filter(
                resource=self.missing_db_resource, locale=self.translated_locale
            ).exists()

    def test_no_project_configuration_extra_locales(self):
        """
        Only create/update the TranslatedResource object for active locales,
        even if the inactive locale has a resource.
        """
        update_translated_resources_without_config(
            self.db_project, self.vcs_project, self.translated_locale,
        )

        assert TranslatedResource.objects.filter(
            resource=self.main_db_resource, locale=self.translated_locale
        ).exists()

        assert TranslatedResource.objects.filter(
            resource=self.other_db_resource, locale=self.translated_locale
        ).exists()

        assert not TranslatedResource.objects.filter(
            resource=self.main_db_resource, locale=self.inactive_locale
        ).exists()

        assert not TranslatedResource.objects.filter(
            resource=self.other_db_resource, locale=self.inactive_locale
        ).exists()


class EntityKeyTests(FakeCheckoutTestCase):
    def test_entity_key_common_string(self):
        """
        Entities with the same string from different resources must not get the
        same key from entity_key.
        """
        assert entity_key(
            self.main_vcs_resource.entities["Common String"]
        ) != entity_key(self.other_vcs_resource.entities["Common String"])


class CommitChangesTests(FakeCheckoutTestCase):
    def setUp(self):
        super(CommitChangesTests, self).setUp()
        self.mock_repo_commit = self.patch_object(Repository, "commit")

    def test_multiple_authors(self):
        """
        Tests if multiple authors are passed to commit message. The
        author with the most occurrences for the locale should be set as
        the commit author.
        """
        first_author, second_author = UserFactory.create_batch(2)
        self.changeset.commit_authors_per_locale = {
            self.translated_locale.code: [first_author, first_author, second_author]
        }
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        commit_changes(
            self.db_project, self.vcs_project, self.changeset, self.translated_locale
        )
        self.repository.commit.assert_called_with(
            CONTAINS(
                first_author.display_name_and_email,
                second_author.display_name_and_email,
            ),
            first_author,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code),
        )

    def test_author_with_multiple_contributions(self):
        """
        Tests if author with multiple contributions occurs once in commit message.
        """
        author = UserFactory.create()
        self.changeset.commit_authors_per_locale = {
            self.translated_locale.code: [author, author]
        }
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        commit_changes(
            self.db_project, self.vcs_project, self.changeset, self.translated_locale
        )
        self.repository.commit.assert_called_with(
            CONTAINS(author.display_name_and_email),
            author,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code),
        )
        commit_message = self.repository.commit.mock_calls[0][1][0]
        assert commit_message.count(author.display_name_and_email) == 1

    def test_no_authors(self):
        """
        If no authors are found in the changeset, default to a fake
        "Mozilla Pontoon" user.
        """
        self.changeset.commit_authors_per_locale = {self.translated_locale.code: []}
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        commit_changes(
            self.db_project, self.vcs_project, self.changeset, self.translated_locale
        )
        self.repository.commit.assert_called_with(
            NOT(CONTAINS("Authors:")),  # Don't list authors in commit
            ANY,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code),
        )
        user = self.mock_repo_commit.call_args[0][1]
        assert user.first_name == "Pontoon"
        assert user.email == "pontoon@example.com"


class PullChangesTests(FakeCheckoutTestCase):
    def setUp(self):
        super(PullChangesTests, self).setUp()
        self.mock_repo_pull = self.patch_object(Repository, "pull")
        self.locales = self.db_project.locales.all()

    def test_basic(self):
        """
        Pull_changes should call repo.pull for each repo for the
        project and return whether any changes happened in VCS.
        """
        mock_db_project = MagicMock()
        mock_db_project.repositories.all.return_value = [self.repository]
        self.mock_repo_pull.return_value = {"single_locale": "asdf"}

        has_changed, _ = pull_locale_repo_changes(self.db_project, self.locales)
        assert has_changed

    def test_unsure_changes(self):
        """
        If any of the repos returns None as a revision number, consider
        the VCS as changed even if the revisions match the last sync.
        """
        self.mock_repo_pull.return_value = {"single_locale": None}
        self.repository.last_synced_revisions = {"single_locale": None}
        self.repository.save()

        has_changed, _ = pull_locale_repo_changes(self.db_project, self.locales)
        assert has_changed

    def test_unchanged(self):
        """
        If the revisions returned by repo.pull match those from the last
        sync, consider the VCS unchanged and return False.
        """
        self.mock_repo_pull.return_value = {"single_locale": "asdf"}
        self.repository.last_synced_revisions = {"single_locale": "asdf"}
        self.repository.save()
        has_changed, _ = pull_locale_repo_changes(
            self.db_project, locales=self.db_project.locales.all()
        )
        assert not has_changed
