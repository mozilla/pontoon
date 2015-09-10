import os.path

from django.core.management.base import CommandError
from django_nose.tools import (
    assert_equal,
    assert_false,
    assert_not_equal,
    assert_not_in,
    assert_raises,
    assert_true
)
from mock import ANY, call, Mock, patch, PropertyMock

from pontoon.administration.management.commands import sync_projects
from pontoon.administration.vcs import CommitToRepositoryException
from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Project,
    Repository,
    Resource,
    Translation,
)
from pontoon.base.tests import (
    assert_attributes_equal,
    ChangedEntityLocaleFactory,
    CONTAINS,
    EntityFactory,
    LocaleFactory,
    NOT,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TestCase,
    TranslationFactory,
    UserFactory,
    VCSEntityFactory,
)
from pontoon.base.utils import aware_datetime
from pontoon.base.vcs_models import VCSProject


FAKE_CHECKOUT_PATH = os.path.join(os.path.dirname(__file__), 'fake-checkout')


class FakeCheckoutTestCase(TestCase):
    """Parent class for tests that use the fake l10n repo checkout."""
    def setUp(self):
        timezone_patch = patch.object(sync_projects, 'timezone')
        self.mock_timezone = timezone_patch.start()
        self.addCleanup(timezone_patch.stop)
        self.mock_timezone.now.return_value = aware_datetime(1970, 1, 1)

        self.translated_locale = LocaleFactory.create(code='translated-locale')
        self.inactive_locale = LocaleFactory.create(code='inactive-locale')
        self.repository = RepositoryFactory()

        self.db_project = ProjectFactory.create(
            name='db-project',
            locales=[self.translated_locale],
            repositories=[self.repository]
        )
        self.main_db_resource = ResourceFactory.create(
            project=self.db_project,
            path='main.lang',
            format='lang'
        )
        self.other_db_resource = ResourceFactory.create(
            project=self.db_project,
            path='other.lang',
            format='lang'
        )
        self.missing_db_resource = ResourceFactory.create(
            project=self.db_project,
            path='missing.lang',
            format='lang'
        )

        # Load paths from the fake locale directory.
        checkout_path_patch = patch.object(
            Project,
            'checkout_path',
            new_callable=PropertyMock,
            return_value=FAKE_CHECKOUT_PATH
        )
        checkout_path_patch.start()
        self.addCleanup(checkout_path_patch.stop)

        self.vcs_project = VCSProject(self.db_project)
        self.main_vcs_resource = self.vcs_project.resources[self.main_db_resource.path]
        self.other_vcs_resource = self.vcs_project.resources[self.other_db_resource.path]
        self.missing_vcs_resource = self.vcs_project.resources[self.missing_db_resource.path]
        self.main_vcs_entity = self.main_vcs_resource.entities['Source String']
        self.main_vcs_translation = self.main_vcs_entity.translations['translated-locale']

        # Mock VCSResource.save() for each resource to avoid altering
        # the filesystem.
        for resource in self.vcs_project.resources.values():
            save_patch = patch.object(resource, 'save')
            save_patch.start()
            self.addCleanup(save_patch.stop)

        self.changeset = sync_projects.ChangeSet(self.db_project, self.vcs_project)

    def create_db_entities_translations(self):
        """
        Create entities and translations in the database for strings
        from the fake checkout.
        """
        self.main_db_entity = EntityFactory.create(
            resource=self.main_db_resource,
            string='Source String',
            key='Source String',
            obsolete=False
        )
        self.other_db_entity = EntityFactory.create(
            resource=self.other_db_resource,
            string='Other Source String',
            key='Other Source String',
            obsolete=False
        )
        self.main_db_translation = TranslationFactory.create(
            entity=self.main_db_entity,
            plural_form=None,
            locale=self.translated_locale,
            string='Translated String',
            date=aware_datetime(1970, 1, 1),
            approved=True,
            extra={'tags': []}
        )


class CommandTests(FakeCheckoutTestCase):
    def setUp(self):
        super(CommandTests, self).setUp()
        self.command = sync_projects.Command()
        self.command.verbosity = 0
        self.command.no_commit = False
        self.command.no_pull = False

        # Avoid hitting VCS during tests by mocking out pull and commit.
        repo_pull_patch = patch.object(Repository, 'pull')
        self.mock_repo_pull = repo_pull_patch.start()
        self.addCleanup(repo_pull_patch.stop)

        repo_commit_patch = patch.object(Repository, 'commit', return_value=None)
        self.mock_repo_commit = repo_commit_patch.start()
        self.addCleanup(repo_commit_patch.stop)

    def execute_command(self, *args, **kwargs):
        kwargs.setdefault('verbosity', 0)
        kwargs.setdefault('no_commit', False)
        kwargs.setdefault('no_pull', False)
        return self.command.handle(*args, **kwargs)

    def test_handle_disabled_projects(self):
        """Only sync projects that aren't disabled."""
        disabled_project = ProjectFactory.create(disabled=True)
        active_project = ProjectFactory.create(disabled=False)
        self.command.handle_project = Mock()
        self.execute_command()

        self.command.handle_project.assert_any_call(active_project)
        assert_not_in(call(disabled_project), self.command.handle_project.mock_calls)

    def test_handle_project_slugs(self):
        """
        If project slugs are passed to Command.handle, only sync projects
        matching those slugs.
        """
        ignore_project, handle_project = ProjectFactory.create_batch(2)
        self.command.handle_project = Mock()
        self.execute_command(handle_project.slug)

        self.command.handle_project.assert_called_with(handle_project)
        assert_not_in(call(ignore_project), self.command.handle_project.mock_calls)

    def test_handle_no_matching_projects(self):
        """
        If no projects are found that match the given slugs, raise a
        CommandError.
        """
        with assert_raises(CommandError):
            self.execute_command('does-not-exist')

    def test_handle_delete_translations(self):
        """
        After syncing, delete any translations that are marked for
        deletion.
        """
        self.create_db_entities_translations()
        self.main_db_translation.deleted = aware_datetime(1970, 1, 1)
        self.main_db_translation.save()

        self.command.handle_project = Mock()
        self.execute_command()
        with assert_raises(Translation.DoesNotExist):
            self.main_db_translation.refresh_from_db()

    def test_handle_cant_commit(self):
        """If project.can_commit is False, do not sync it."""
        with patch.object(Project, 'can_commit', new_callable=PropertyMock) as can_commit:
            can_commit.return_value = False
            self.command.handle_project = Mock()

            self.execute_command(self.db_project.slug)
            assert_false(self.command.handle_project.called)

    def test_handle_project_handle_entities(self):
        """Call handle_entity on all matching Entity and VCSEntity pairs."""
        vcs_entities = {
            'match': VCSEntityFactory(),
            'no_db_match': VCSEntityFactory()
        }
        self.command.get_vcs_entities = Mock(return_value=vcs_entities)
        db_entities = {
            'match': EntityFactory(),
            'no_vcs_match': EntityFactory()
        }
        self.command.get_db_entities = Mock(return_value=db_entities)
        self.command.handle_entity = Mock()

        self.command.handle_project(self.db_project)
        self.command.handle_entity.assert_has_calls([
            call(ANY, self.db_project, 'match', db_entities['match'], vcs_entities['match']),
            call(ANY, self.db_project, 'no_vcs_match', db_entities['no_vcs_match'], None),
            call(ANY, self.db_project, 'no_db_match', None, vcs_entities['no_db_match']),
        ], any_order=True)

    def test_handle_project_clear_changed_entities(self):
        """
        Delete all ChangedEntityLocale objects for the project after
        handling it.
        """
        changed1, changed2 = ChangedEntityLocaleFactory.create_batch(2,
            locale=self.translated_locale,
            entity__resource__project=self.db_project
        )

        self.command.handle_project(self.db_project)
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed1.refresh_from_db()
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed2.refresh_from_db()

    def test_handle_project_no_commit(self):
        """Don't call commit_projects if command.no_commit is True."""
        self.command.commit_projects = Mock()
        self.command.no_commit = True
        self.command.handle_project(self.db_project)
        assert_false(self.command.commit_projects.called)

    def test_handle_project_no_pull(self):
        """
        Don't call repo.pull if command.no_pull is True.
        """
        self.command.no_pull = True
        self.command.handle_project(self.db_project)
        assert_false(self.mock_repo_pull.called)

    def call_handle_entity(self, key, db_entity, vcs_entity):
        return self.command.handle_entity(
            self.changeset, self.db_project, key, db_entity, vcs_entity
        )

    def test_handle_entity_none(self):
        """
        If both the db_entity and vcs_entity are None, raise a
        CommandError, as that should never happen.
        """
        with assert_raises(CommandError):
            self.call_handle_entity('key', None, None)

    def test_handle_entity_obsolete(self):
        """If VCS is missing the entity in question, obsolete it."""
        self.create_db_entities_translations()
        self.changeset.obsolete_db_entity = Mock()
        self.call_handle_entity('key', self.main_db_entity, None)
        self.changeset.obsolete_db_entity.assert_called_with(self.main_db_entity)

    def test_handle_entity_create(self):
        """If the DB is missing an entity in VCS, create it."""
        self.create_db_entities_translations()
        self.changeset.create_db_entity = Mock()
        self.call_handle_entity('key', None, self.main_vcs_entity)
        self.changeset.create_db_entity.assert_called_with(self.main_vcs_entity)

    def test_handle_entity_no_translation(self):
        """If no translation exists for a specific locale, skip it."""
        self.create_db_entities_translations()
        self.changeset.update_vcs_entity = Mock()
        self.changeset.update_db_entity = Mock()
        self.main_vcs_entity.has_translation_for = Mock(return_value=False)

        self.call_handle_entity('key', self.main_db_entity, self.main_vcs_entity)
        assert_false(self.changeset.update_vcs_entity.called)
        assert_false(self.changeset.update_db_entity.called)

    def test_handle_entity_db_changed(self):
        """
        If the DB entity has changed since the last sync, update the
        VCS.
        """
        self.create_db_entities_translations()
        self.changeset.update_vcs_entity = Mock()
        with patch.object(Entity, 'has_changed', return_value=True):
            self.call_handle_entity('key', self.main_db_entity, self.main_vcs_entity)

        self.changeset.update_vcs_entity.assert_called_with(
            self.translated_locale.code, self.main_db_entity, self.main_vcs_entity
        )

    def test_handle_entity_vcs_changed(self):
        """
        If the DB entity has not changed since the last sync, update the DB with
        the latest changes from VCS.
        """
        self.create_db_entities_translations()
        self.changeset.update_db_entity = Mock()
        with patch.object(Entity, 'has_changed', return_value=False):
            self.call_handle_entity('key', self.main_db_entity, self.main_vcs_entity)

        self.changeset.update_db_entity.assert_called_with(
            self.translated_locale.code, self.main_db_entity, self.main_vcs_entity
        )

    def test_update_resources(self):
        # Check for self.main_db_resource to be updated and
        # self.other_db_resource to be created.
        self.main_db_resource.entity_count = 5000
        self.main_db_resource.save()
        self.other_db_resource.delete()

        self.command.update_resources(self.db_project, self.vcs_project)
        self.main_db_resource.refresh_from_db()
        assert_equal(self.main_db_resource.entity_count, len(self.main_vcs_resource.entities))

        other_db_resource = Resource.objects.get(path=self.other_vcs_resource.path)
        assert_equal(other_db_resource.entity_count, len(self.other_vcs_resource.entities))

    def test_update_stats(self):
        """
        Call update_stats on all resources available in the current
        locale.
        """
        with patch.object(sync_projects, 'update_stats') as update_stats:
            self.command.update_stats(self.db_project, self.vcs_project, self.changeset)

            update_stats.assert_any_call(self.main_db_resource, self.translated_locale)
            update_stats.assert_any_call(self.other_db_resource, self.translated_locale)
            assert_not_in(
                call(self.missing_db_resource, self.translated_locale),
                update_stats.mock_calls
            )

    def test_update_stats_asymmetric(self):
        """
        Call update_stats on asymmetric resources even if they don't
        exist in the target locale.
        """
        update_stats_patch = patch.object(sync_projects, 'update_stats')
        is_asymmetric_patch = patch.object(Resource, 'is_asymmetric', new_callable=PropertyMock)
        with update_stats_patch as update_stats, is_asymmetric_patch as is_asymmetric:
            is_asymmetric.return_value = True

            self.command.update_stats(self.db_project, self.vcs_project, self.changeset)
            update_stats.assert_any_call(self.main_db_resource, self.translated_locale)
            update_stats.assert_any_call(self.other_db_resource, self.translated_locale)
            update_stats.assert_any_call(self.missing_db_resource, self.translated_locale)

    def test_update_stats_extra_locales(self):
        """
        Only update stats for active locales, even if the inactive
        locale has a resource.
        """
        with patch.object(sync_projects, 'update_stats') as update_stats:
            self.command.update_stats(self.db_project, self.vcs_project, self.changeset)

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

    def test_entity_key_common_string(self):
        """
        Entities with the same string from different resources must not get the
        same key from entity_key.
        """
        assert_not_equal(
            self.command.entity_key(self.main_vcs_resource.entities['Common String']),
            self.command.entity_key(self.other_vcs_resource.entities['Common String'])
        )

    def test_commit_changes(self):
        user = UserFactory.create()
        self.changeset.commit_authors_per_locale = {
            self.translated_locale.code: [user]
        }
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        self.command.commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.repository.commit.assert_called_with(
            CONTAINS(user.display_name),
            user,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code)
        )

    def test_commit_changes_no_authors(self):
        """
        If no authors are found in the changeset, default to a fake
        "Pontoon" user.
        """
        self.changeset.commit_authors_per_locale = {
            self.translated_locale.code: []
        }
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        self.command.commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.repository.commit.assert_called_with(
            NOT(CONTAINS('Authors:')),  # Don't list authors in commit
            ANY,
            os.path.join(FAKE_CHECKOUT_PATH, self.translated_locale.code)
        )
        user = self.mock_repo_commit.call_args[0][1]
        assert_equal(user.first_name, 'Pontoon')
        assert_equal(user.email, 'pontoon@mozilla.com')

    def test_commit_changes_error(self):
        """If commit_changes returns an error object, log it."""
        self.command.stdout = Mock()
        self.repository.commit.return_value = {'message': 'Whoops!'}
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        self.command.commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.command.stdout.write.assert_called_with(
            CONTAINS('db-project', 'failed', 'Whoops!')
        )

    def test_commit_changes_raised_committorepositoryexception(self):
        """
        If repo.commit raises a CommitToRepositoryException, log it.
        """
        self.command.stdout = Mock()
        self.repository.commit.side_effect = CommitToRepositoryException('Whoops!')
        self.db_project.repository_for_path = Mock(return_value=self.repository)

        self.command.commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.command.stdout.write.assert_called_with(
            CONTAINS('db-project', 'failed', 'Whoops!')
        )

    def test_commit_changes_raised_valueerror(self):
        """
        If db_project.repository_for_path raises a ValueError, log it.
        """
        self.command.stdout = Mock()
        self.db_project.repository_for_path = Mock(side_effect=ValueError('Whoops!'))

        self.command.commit_changes(self.db_project, self.vcs_project, self.changeset)
        self.command.stdout.write.assert_called_with(
            CONTAINS('db-project', 'failed', 'Whoops!')
        )


class ChangeSetTests(FakeCheckoutTestCase):
    def test_execute_called_once(self):
        """Raise a RuntimeError if execute is called more than once."""
        self.changeset.execute()
        with assert_raises(RuntimeError):
            self.changeset.execute()

    def update_main_vcs_entity(self, **translation_changes):
        self.create_db_entities_translations()

        for key, value in translation_changes.items():
            setattr(self.main_db_translation, key, value)
        self.main_db_translation.save()

        self.changeset.update_vcs_entity(
            self.translated_locale.code,
            self.main_db_entity,
            self.main_vcs_entity
        )
        self.changeset.execute()

    def test_update_vcs_entity(self):
        """
        Update the VCS translations with translations in the database.
        """
        self.update_main_vcs_entity(string='New Translated String')
        assert_equal(self.main_vcs_translation.strings, {None: 'New Translated String'})

        # Ensure only resources that were updated are saved.
        assert_true(self.main_vcs_resource.save.called)
        assert_false(self.other_vcs_resource.save.called)

        # Update the VCS translation with info about the last
        # translation.
        assert_equal(self.main_vcs_translation.last_updated, self.main_db_translation.date)
        assert_equal(self.main_vcs_translation.last_translator, self.main_db_translation.user)

    def test_update_vcs_entity_unapproved(self):
        """
        Do not update VCS with unapproved translations. If no approved
        translations exist, delete existing ones.
        """
        self.update_main_vcs_entity(approved=False)
        assert_equal(self.main_vcs_translation.strings, {})

    def test_update_vcs_entity_fuzzy(self):
        self.main_vcs_translation.fuzzy = False
        self.update_main_vcs_entity(fuzzy=True)
        assert_equal(self.main_vcs_translation.fuzzy, True)

    def test_update_vcs_entity_not_fuzzy(self):
        self.main_vcs_translation.fuzzy = True
        self.update_main_vcs_entity(fuzzy=False)
        assert_equal(self.main_vcs_translation.fuzzy, False)

    def test_update_vcs_last_translation_no_translations(self):
        """
        If there are no translations in the database, do not set the
        last_updated and last_translator fields on the VCS translation.
        """
        self.create_db_entities_translations()
        self.main_db_translation.delete()

        self.changeset.update_vcs_entity(
            self.translated_locale.code,
            self.main_db_entity,
            self.main_vcs_entity
        )
        self.changeset.execute()

        assert_equal(self.main_vcs_translation.last_updated, None)
        assert_equal(self.main_vcs_translation.last_translator, None)

    def test_update_vcs_entity_user(self):
        """Track translation authors for use in the commit message."""
        user = UserFactory.create()
        self.update_main_vcs_entity(user=user)
        assert_equal(self.changeset.commit_authors_per_locale['translated-locale'], [user])

    def test_create_db(self):
        """Create new entity in the database."""
        self.main_vcs_entity.key = 'string-key'
        self.main_vcs_entity.comments = ['first comment', 'second']
        self.main_vcs_entity.order = 7
        self.main_vcs_translation.fuzzy = False
        self.main_vcs_entity.string_plural = 'plural string'
        self.main_vcs_entity.source = ['foo.py:87']

        self.changeset.create_db_entity(self.main_vcs_entity)
        self.changeset.execute()
        new_entity = Entity.objects.get(
            resource__path=self.main_vcs_resource.path,
            string=self.main_vcs_entity.string
        )
        assert_attributes_equal(
            new_entity,
            resource=self.main_db_resource,
            string='Source String',
            key='string-key',
            comment='first comment\nsecond',
            order=7,
            string_plural='plural string',
            source=['foo.py:87'],
        )

        new_translation = new_entity.translation_set.all()[0]
        assert_attributes_equal(
            new_translation,
            locale=self.translated_locale,
            string='Translated String',
            plural_form=None,
            approved=True,
            approved_date=aware_datetime(1970, 1, 1),
            fuzzy=False
        )

    def update_main_db_entity(self):
        self.changeset.update_db_entity(
            self.translated_locale.code,
            self.main_db_entity,
            self.main_vcs_entity
        )
        self.changeset.execute()

    def test_update_db_existing_translation(self):
        """
        Update an existing translation in the DB with changes from VCS.
        """
        self.create_db_entities_translations()

        # Set up DB and VCS to differ and require an update.
        self.main_db_translation.fuzzy = True
        self.main_db_translation.extra = {}
        self.main_db_translation.save()

        self.main_vcs_entity.key = 'string-key'
        self.main_vcs_entity.comments = ['first comment', 'second']
        self.main_vcs_entity.order = 7
        self.main_vcs_entity.string_plural = 'plural string'
        self.main_vcs_entity.source = ['foo.py:87']
        self.main_vcs_translation.fuzzy = False
        # The test translation is from a langfile so we can use tags
        # for testing extra.
        self.main_vcs_translation.tags = set(['ok'])

        self.update_main_db_entity()
        self.main_db_entity.refresh_from_db()
        assert_attributes_equal(
            self.main_db_entity,
            key='string-key',
            comment='first comment\nsecond',
            order=7,
            string_plural='plural string',
            source=['foo.py:87'],
        )

        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation,
            fuzzy=False,
            extra={'tags': ['ok']}
        )

    def test_update_db_clean_entity_translation(self):
        """
        If no changes have been made to the database entity or the
        translation, do not bother updating them in the database.
        """
        self.create_db_entities_translations()
        self.update_main_db_entity()

        # TODO: It'd be nice if we didn't rely on internal changeset
        # attributes to check this, but not vital.
        assert_not_in(self.main_db_entity, self.changeset.entities_to_update)
        assert_not_in(self.main_db_translation, self.changeset.translations_to_update)

    def test_update_db_approve_translation(self):
        """
        Approve any un-approved translations that have counterparts in
        VCS.
        """
        self.create_db_entities_translations()
        self.main_db_translation.approved = False
        self.main_db_translation.approved_date = None
        self.main_db_translation.save()

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation,
            approved=True,
            approved_date=aware_datetime(1970, 1, 1)
        )

    def test_update_db_new_translation(self):
        """
        If a matching translation does not exist in the database, create a new
        one.
        """
        self.create_db_entities_translations()
        self.main_db_translation.delete()
        self.update_main_db_entity()

        translation = self.main_db_entity.translation_set.all()[0]
        assert_attributes_equal(
            translation,
            locale=self.translated_locale,
            string='Translated String',
            plural_form=None,
            approved=True,
            approved_date=aware_datetime(1970, 1, 1),
            fuzzy=False,
            extra={'tags': []}
        )

    def test_update_db_unapprove_existing(self):
        """
        Any existing translations that don't match anything in VCS get
        unapproved.
        """
        self.create_db_entities_translations()

        self.main_db_translation.approved = True
        self.main_db_translation.approved_date = aware_datetime(1970, 1, 1)
        self.main_db_translation.approved_user = UserFactory.create()
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = 'New Translated String'

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_attributes_equal(
            self.main_db_translation,
            approved=False,
            approved_user=None,
            approved_date=None
        )

    def test_update_db_unapprove_clean(self):
        """
        If translations that are set to be unapproved were already unapproved,
        don't bother updating them.
        """
        self.create_db_entities_translations()

        self.main_db_translation.approved = False
        self.main_db_translation.approved_date = None
        self.main_db_translation.approved_user = None
        self.main_db_translation.save()
        self.main_vcs_translation.strings[None] = 'New Translated String'

        self.update_main_db_entity()
        self.main_db_translation.refresh_from_db()
        assert_not_in(self.main_db_translation, self.changeset.translations_to_update)

    def test_obsolete_db(self):
        self.create_db_entities_translations()
        self.changeset.obsolete_db_entity(self.main_db_entity)
        self.changeset.execute()
        self.main_db_entity.refresh_from_db()
        assert_true(self.main_db_entity.obsolete)
