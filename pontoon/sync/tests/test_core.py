import os.path

from django_nose.tools import (
    assert_equal,
    assert_false,
    assert_not_equal,
    assert_not_in,
    assert_raises,
    assert_true
)
from mock import ANY, call, Mock, patch, PropertyMock

from pontoon.administration.vcs import CommitToRepositoryException
from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Project,
    Repository,
    Resource,
)
from pontoon.base.tests import (
    ChangedEntityLocaleFactory,
    CONTAINS,
    EntityFactory,
    NOT,
    TranslationFactory,
    UserFactory,
)
from pontoon.base.utils import aware_datetime
from pontoon.sync.core import (
    commit_changes,
    entity_key,
    handle_entity,
    pull_changes,
    sync_project,
    update_project_stats,
    update_resources,
)
from pontoon.sync.tests import FAKE_CHECKOUT_PATH, FakeCheckoutTestCase, VCSEntityFactory


class SyncProjectTests(FakeCheckoutTestCase):
    def setUp(self):
        super(SyncProjectTests, self).setUp()
        self.mock_pull_changes = self.patch('pontoon.sync.core.pull_changes', return_value=True)
        self.mock_commit_changes = self.patch('pontoon.sync.core.commit_changes')
        self.mock_project_needs_sync = self.patch_object(
            Project, 'needs_sync', new_callable=PropertyMock, return_value=True)

    def test_db_changed_no_repo_changed(self):
        """
        If the database has changes and VCS doesn't, do not skip syncing
        the project.
        """
        self.mock_pull_changes.return_value = False
        self.mock_project_needs_sync.return_value = True

        with patch('pontoon.sync.core.handle_entity') as mock_handle_entity:
            sync_project(self.db_project)
        assert_true(mock_handle_entity.called)

    def test_no_changes_skip(self):
        """
        If the database and VCS both have no changes, skip sync and log
        a message.
        """
        self.mock_pull_changes.return_value = False
        self.mock_project_needs_sync.return_value = False

        with patch('pontoon.sync.core.log') as mock_log, \
             patch('pontoon.sync.core.handle_entity') as mock_handle_entity:
            sync_project(self.db_project)

        assert_false(mock_handle_entity.called)
        mock_log.info.assert_called_with(
            CONTAINS('Skipping', self.db_project.slug)
        )

    def test_handle_entities(self):
        """Call handle_entity on all matching Entity and VCSEntity pairs."""
        vcs_entities = {
            'match': VCSEntityFactory(),
            'no_db_match': VCSEntityFactory()
        }
        db_entities = {
            'match': EntityFactory(),
            'no_vcs_match': EntityFactory()
        }

        with patch('pontoon.sync.core.get_vcs_entities', return_value=vcs_entities), \
             patch('pontoon.sync.core.get_db_entities', return_value=db_entities), \
             patch('pontoon.sync.core.handle_entity') as mock_handle_entity:
            sync_project(self.db_project)

        mock_handle_entity.assert_has_calls([
            call(ANY, self.db_project, 'match', db_entities['match'], vcs_entities['match']),
            call(ANY, self.db_project, 'no_vcs_match', db_entities['no_vcs_match'], None),
            call(ANY, self.db_project, 'no_db_match', None, vcs_entities['no_db_match']),
        ], any_order=True)

    def test_clear_changed_entities(self):
        """
        Delete all ChangedEntityLocale objects for the project created
        before the sync started after handling it.
        """
        self.mock_timezone.return_value = aware_datetime(1970, 1, 2)
        changed1, changed2, changed_after = ChangedEntityLocaleFactory.create_batch(3,
            locale=self.translated_locale,
            entity__resource=self.main_db_resource,
            entity__resource__project=self.db_project,
            when=aware_datetime(1970, 1, 1)
        )
        changed_after.when = aware_datetime(1970, 1, 3)
        changed_after.save()

        sync_project(self.db_project)
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed1.refresh_from_db()
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed2.refresh_from_db()
        changed_after.refresh_from_db()  # Should not raise

    def test_reset_project_has_changed(self):
        """After syncing, set db_project.has_changed to False."""
        self.db_project.has_changed = True
        self.db_project.save()

        sync_project(self.db_project)
        self.db_project.refresh_from_db()
        assert_false(self.db_project.has_changed)

    def test_no_commit(self):
        """Don't call commit_changes if command.no_commit is True."""
        with patch('pontoon.sync.core.commit_changes') as mock_commit_changes:
            sync_project(self.db_project, no_commit=True)
        assert_false(mock_commit_changes.called)

    def test_no_pull(self):
        """
        Don't call repo.pull if command.no_pull is True.
        """
        sync_project(self.db_project, no_pull=True)
        assert_false(self.mock_pull_changes.called)

    def test_remove_duplicate_approvals(self):
        """
        Ensure that duplicate approvals are removed.
        """
        # Trigger creation of new approved translation.
        self.main_vcs_translation.strings[None] = 'New Translated String'
        self.main_vcs_translation.fuzzy = False

        # Translation approved after the sync started simulates the race
        # where duplicate translations occur.
        duplicate_translation = TranslationFactory.create(
            entity=self.main_db_entity,
            locale=self.translated_locale,
            string='Other New Translated String',
            approved=True,
            approved_date=aware_datetime(1970, 1, 3)
        )
        ChangedEntityLocale.objects.filter(entity=self.main_db_entity).delete()

        with patch('pontoon.sync.core.VCSProject', return_value=self.vcs_project):
            sync_project(self.db_project)

        # Only one translation should be approved: the duplicate_translation.
        assert_equal(self.main_db_entity.translation_set.filter(approved=True).count(), 1)
        new_translation = self.main_db_entity.translation_set.get(
            string='New Translated String'
        )
        assert_false(new_translation.approved)
        assert_true(new_translation.approved_date is None)

        duplicate_translation.refresh_from_db()
        assert_true(duplicate_translation.approved)
        assert_equal(duplicate_translation.approved_date, aware_datetime(1970, 1, 3))


class HandleEntityTests(FakeCheckoutTestCase):
    def call_handle_entity(self, key, db_entity, vcs_entity):
        return handle_entity(
            self.changeset, self.db_project, key, db_entity, vcs_entity
        )

    def test_none(self):
        """
        If both the db_entity and vcs_entity are None, raise a
        CommandError, as that should never happen.
        """
        with assert_raises(ValueError):
            self.call_handle_entity('key', None, None)

    def test_obsolete(self):
        """If VCS is missing the entity in question, obsolete it."""
        self.changeset.obsolete_db_entity = Mock()
        self.call_handle_entity('key', self.main_db_entity, None)
        self.changeset.obsolete_db_entity.assert_called_with(self.main_db_entity)

    def test_create(self):
        """If the DB is missing an entity in VCS, create it."""
        self.changeset.create_db_entity = Mock()
        self.call_handle_entity('key', None, self.main_vcs_entity)
        self.changeset.create_db_entity.assert_called_with(self.main_vcs_entity)

    def test_no_translation(self):
        """If no translation exists for a specific locale, skip it."""
        self.changeset.update_vcs_entity = Mock()
        self.changeset.update_db_entity = Mock()
        self.main_vcs_entity.has_translation_for = Mock(return_value=False)

        self.call_handle_entity('key', self.main_db_entity, self.main_vcs_entity)
        assert_false(self.changeset.update_vcs_entity.called)
        assert_false(self.changeset.update_db_entity.called)

    def test_db_changed(self):
        """
        If the DB entity has changed since the last sync, update the
        VCS.
        """
        self.changeset.update_vcs_entity = Mock()
        with patch.object(Entity, 'has_changed', return_value=True):
            self.call_handle_entity('key', self.main_db_entity, self.main_vcs_entity)

        self.changeset.update_vcs_entity.assert_called_with(
            self.translated_locale.code, self.main_db_entity, self.main_vcs_entity
        )

    def test_vcs_changed(self):
        """
        If the DB entity has not changed since the last sync, update the DB with
        the latest changes from VCS.
        """
        self.changeset.update_db_entity = Mock()
        with patch.object(Entity, 'has_changed', return_value=False):
            self.call_handle_entity('key', self.main_db_entity, self.main_vcs_entity)

        self.changeset.update_db_entity.assert_called_with(
            self.translated_locale.code, self.main_db_entity, self.main_vcs_entity
        )


class UpdateResourcesTests(FakeCheckoutTestCase):
    def test_basic(self):
        # Check for self.main_db_resource to be updated and
        # self.other_db_resource to be created.
        self.main_db_resource.entity_count = 5000
        self.main_db_resource.save()
        self.other_db_resource.delete()

        update_resources(self.db_project, self.vcs_project)
        self.main_db_resource.refresh_from_db()
        assert_equal(self.main_db_resource.entity_count, len(self.main_vcs_resource.entities))

        other_db_resource = Resource.objects.get(path=self.other_vcs_resource.path)
        assert_equal(other_db_resource.entity_count, len(self.other_vcs_resource.entities))


class UpdateProjectStatsTests(FakeCheckoutTestCase):
    def test_basic(self):
        """
        Call update_stats on all resources available in the current
        locale.
        """
        with patch('pontoon.sync.core.update_stats') as update_stats:
            update_project_stats(self.db_project, self.vcs_project, self.changeset)

            update_stats.assert_any_call(self.main_db_resource, self.translated_locale)
            update_stats.assert_any_call(self.other_db_resource, self.translated_locale)
            assert_not_in(
                call(self.missing_db_resource, self.translated_locale),
                update_stats.mock_calls
            )

    def test_asymmetric(self):
        """
        Call update_stats on asymmetric resources even if they don't
        exist in the target locale.
        """
        with patch('pontoon.sync.core.update_stats') as update_stats, \
             patch.object(Resource, 'is_asymmetric', new_callable=PropertyMock) as is_asymmetric:
            is_asymmetric.return_value = True

            update_project_stats(self.db_project, self.vcs_project, self.changeset)
            update_stats.assert_any_call(self.main_db_resource, self.translated_locale)
            update_stats.assert_any_call(self.other_db_resource, self.translated_locale)
            update_stats.assert_any_call(self.missing_db_resource, self.translated_locale)

    def test_extra_locales(self):
        """
        Only update stats for active locales, even if the inactive
        locale has a resource.
        """
        with patch('pontoon.sync.core.update_stats') as update_stats:
            update_project_stats(self.db_project, self.vcs_project, self.changeset)

            update_stats.assert_any_call(self.main_db_resource, self.translated_locale)
            update_stats.assert_any_call(self.other_db_resource, self.translated_locale)
            assert_not_in(
                call(self.main_db_resource, self.inactive_locale),
                update_stats.mock_calls
            )
            assert_not_in(
                call(self.other_db_resource, self.inactive_locale),
                update_stats.mock_calls
            )


class EntityKeyTests(FakeCheckoutTestCase):
    def test_entity_key_common_string(self):
        """
        Entities with the same string from different resources must not get the
        same key from entity_key.
        """
        assert_not_equal(
            entity_key(self.main_vcs_resource.entities['Common String']),
            entity_key(self.other_vcs_resource.entities['Common String'])
        )


class CommitChangesTests(FakeCheckoutTestCase):
    def setUp(self):
        super(CommitChangesTests, self).setUp()
        self.mock_repo_commit = self.patch_object(Repository, 'commit')

    def test_multiple_authors(self):
        """
        Tests if multiple authors are passed to commit message.
        """
        first_author, second_author = UserFactory.create_batch(2)
        self.changeset.commit_authors_per_locale = {
            self.translated_locale.code: [first_author, second_author]
        }
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.repository.commit.assert_called_with(
            CONTAINS(first_author.display_name, second_author.display_name),
            second_author,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code)
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

        commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.repository.commit.assert_called_with(
            CONTAINS(author.display_name),
            author,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code)
        )
        commit_message = self.repository.commit.mock_calls[0][1][0]
        assert_equal(commit_message.count(author.display_name), 1)

    def test_no_authors(self):
        """
        If no authors are found in the changeset, default to a fake
        "Pontoon" user.
        """
        self.changeset.commit_authors_per_locale = {
            self.translated_locale.code: []
        }
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.repository.commit.assert_called_with(
            NOT(CONTAINS('Authors:')),  # Don't list authors in commit
            ANY,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code)
        )
        user = self.mock_repo_commit.call_args[0][1]
        assert_equal(user.first_name, 'Pontoon')
        assert_equal(user.email, 'pontoon@mozilla.com')

    def test_error(self):
        """If commit_changes returns an error object, log it."""
        self.repository.commit.return_value = {'message': 'Whoops!'}
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        with patch('pontoon.sync.core.log') as mock_log:
            commit_changes(self.db_project, self.vcs_project, self.changeset)

        mock_log.info.assert_called_with(
            CONTAINS('db-project', 'failed', 'Whoops!')
        )

    def test_raised_committorepositoryexception(self):
        """
        If repo.commit raises a CommitToRepositoryException, log it.
        """
        self.repository.commit.side_effect = CommitToRepositoryException('Whoops!')
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        with patch('pontoon.sync.core.log') as mock_log:
            commit_changes(self.db_project, self.vcs_project, self.changeset)

        mock_log.info.assert_called_with(
            CONTAINS('db-project', 'failed', 'Whoops!')
        )

    def test_raised_valueerror(self):
        """
        If db_project.repository_for_path raises a ValueError, log it.
        """
        self.db_project.repository_for_path = Mock(side_effect=ValueError('Whoops!'))

        with patch('pontoon.sync.core.log') as mock_log:
            commit_changes(self.db_project, self.vcs_project, self.changeset)

        mock_log.info.assert_called_with(
            CONTAINS('db-project', 'failed', 'Whoops!')
        )


class PullChangesTests(FakeCheckoutTestCase):
    def setUp(self):
        super(PullChangesTests, self).setUp()
        self.mock_repo_pull = self.patch_object(Repository, 'pull')

    def test_basic(self):
        """
        Pull_changes should call repo.pull for each repo for the
        project, save the return value to repo.last_synced_revisions,
        and return whether any changes happened in VCS.
        """
        self.mock_repo_pull.return_value = {'single_locale': 'asdf'}
        assert_true(pull_changes(self.db_project))
        self.repository.refresh_from_db()
        assert_equal(self.repository.last_synced_revisions, {'single_locale': 'asdf'})

    def test_unsure_changes(self):
        """
        If any of the repos returns None as a revision number, consider
        the VCS as changed even if the revisions match the last sync.
        """
        self.mock_repo_pull.return_value = {'single_locale': None}
        self.repository.last_synced_revisions = {'single_locale': None}
        self.repository.save()

        assert_true(pull_changes(self.db_project))

    def test_unchanged(self):
        """
        If the revisions returned by repo.pull match those from the last
        sync, consider the VCS unchanged and return False.
        """
        self.mock_repo_pull.return_value = {'single_locale': 'asdf'}
        self.repository.last_synced_revisions = {'single_locale': 'asdf'}
        self.repository.save()

        assert_false(pull_changes(self.db_project))
