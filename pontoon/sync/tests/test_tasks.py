from __future__ import absolute_import

from django_nose.tools import assert_equal, assert_false, assert_raises, assert_true
from mock import ANY, patch, PropertyMock

from pontoon.base.models import ChangedEntityLocale, Locale, Project, Repository
from pontoon.base.tests import (
    ChangedEntityLocaleFactory,
    CONTAINS,
    ProjectFactory,
    RepositoryFactory,
    TestCase,
    TranslationFactory,
)
from pontoon.base.utils import aware_datetime
from pontoon.sync.core import serial_task
from pontoon.sync.models import ProjectSyncLog, RepositorySyncLog, SyncLog
from pontoon.sync.tasks import sync_project, sync_translations
from pontoon.sync.tests import (
    FAKE_CHECKOUT_PATH,
    FakeCheckoutTestCase,
    ProjectSyncLogFactory,
    SyncLogFactory,
)


class SyncProjectTests(TestCase):
    def setUp(self):
        super(SyncProjectTests, self).setUp()
        self.db_project = ProjectFactory.create()
        self.repository = self.db_project.repositories.all()[0]
        self.sync_log = SyncLogFactory.create()

        self.mock_pull_changes = self.patch(
            'pontoon.sync.tasks.pull_changes', return_value=[True, {}]
        )
        self.mock_project_needs_sync = self.patch_object(
            Project, 'needs_sync', new_callable=PropertyMock, return_value=True)

        self.mock_sync_translations = self.patch('pontoon.sync.tasks.sync_translations')

        self.mock_update_originals = self.patch(
            'pontoon.sync.tasks.update_originals',
            return_value=[[], [], []]
        )

        self.mock_source_directory_path = self.patch(
            'pontoon.sync.vcs.models.VCSProject.source_directory_path',
            return_value=self.repository.checkout_path
        )

    def test_missing_project(self):
        """
        If a project with the given PK doesn't exist, log it and exit.
        """
        with patch('pontoon.sync.tasks.log') as mock_log:
            with assert_raises(Project.DoesNotExist):
                sync_project(99999, self.sync_log.pk)
            mock_log.error.assert_called_with(CONTAINS('99999'))
            assert_false(self.mock_update_originals.called)

    def test_missing_log(self):
        """
        If a log with the given PK doesn't exist, log it and exit.
        """
        with patch('pontoon.sync.tasks.log') as mock_log:
            with assert_raises(SyncLog.DoesNotExist):
                sync_project(self.db_project.pk, 99999)
            mock_log.error.assert_called_with(CONTAINS('99999'))
            assert_false(self.mock_update_originals.called)

    def test_db_changed_no_repo_changed(self):
        """
        If the database has changes and VCS doesn't, skip syncing
        resources, but sync translations.
        """
        self.mock_pull_changes.return_value = [False, {}]
        self.mock_project_needs_sync.return_value = True

        with patch('pontoon.sync.tasks.log') as mock_log:
            sync_project(self.db_project.pk, self.sync_log.pk)

        sync_project(self.db_project.pk, self.sync_log.pk)
        assert_false(self.mock_update_originals.called)
        mock_log.info.assert_called_with(
            CONTAINS('Skipping syncing sources', self.db_project.slug)
        )

    def test_no_changes_skip(self):
        """
        If the database and the source repository both have no
        changes, and project has a single repository, skip sync.
        """
        self.mock_pull_changes.return_value = [False, {}]
        self.mock_project_needs_sync.return_value = False

        with patch('pontoon.sync.tasks.log') as mock_log:
            sync_project(self.db_project.pk, self.sync_log.pk)

        assert_false(self.mock_update_originals.called)
        mock_log.info.assert_called_with(
            CONTAINS('Skipping project', self.db_project.slug)
        )

        # When skipping, mark the project log properly.
        assert_true(ProjectSyncLog.objects.get(project=self.db_project).skipped)

    def test_no_changes_force(self):
        """
        If the database and VCS both have no changes, but force is true,
        do not skip syncing resources.
        """
        self.mock_pull_changes.return_value = [False, {}]
        self.mock_project_needs_sync.return_value = False

        sync_project(self.db_project.pk, self.sync_log.pk, force=True)
        assert_true(self.mock_update_originals.called)

    def test_no_pull(self):
        """
        Don't call repo.pull if command.no_pull is True.
        """
        sync_project(self.db_project.pk, self.sync_log.pk, no_pull=True)
        assert_false(self.mock_pull_changes.called)

    def test_create_project_log(self):
        assert_false(ProjectSyncLog.objects.exists())
        sync_project(self.db_project.pk, self.sync_log.pk)

        log = ProjectSyncLog.objects.get(project=self.db_project)
        assert_equal(self.mock_sync_translations.delay.call_args[0][1], log.pk)


class SyncTranslationsTests(FakeCheckoutTestCase):
    def setUp(self):
        super(SyncTranslationsTests, self).setUp()
        self.project_sync_log = ProjectSyncLogFactory.create()

        self.mock_pull_changes = self.patch(
            'pontoon.sync.tasks.pull_changes', return_value=[True, {}])
        self.mock_commit_changes = self.patch('pontoon.sync.tasks.commit_changes')
        self.mock_repo_checkout_path = self.patch_object(
            Repository, 'checkout_path', new_callable=PropertyMock,
            return_value=FAKE_CHECKOUT_PATH)

    def test_clear_changed_entities(self):
        """
        Delete all ChangedEntityLocale objects for the project created
        before the sync started after handling it.
        """
        self.now = aware_datetime(1970, 1, 2)
        self.mock_pull_changes.return_value = [True, {
            self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)
        }]

        changed1, changed2, changed_after = ChangedEntityLocaleFactory.create_batch(
            3,
            locale=self.translated_locale,
            entity__resource=self.main_db_resource,
            when=aware_datetime(1970, 1, 1)
        )
        changed_after.when = aware_datetime(1970, 1, 3)
        changed_after.save()

        sync_translations(self.db_project.pk, self.project_sync_log.pk,
                          self.now)
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed1.refresh_from_db()
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed2.refresh_from_db()
        changed_after.refresh_from_db()  # Should not raise

    def test_no_commit(self):
        """Don't call commit_changes if command.no_commit is True."""
        self.mock_pull_changes.return_value = [True, {
            self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)
        }]
        sync_translations(self.db_project.pk, self.project_sync_log.pk,
                          self.now, no_commit=True)
        assert_false(self.mock_commit_changes.called)

    def test_readonly_locales(self):
        """Don't call commit_changes for locales in read-only mode."""
        project_locale = self.translated_locale.project_locale.get(
            project=self.db_project,
        )
        project_locale.readonly = True
        project_locale.save()

        self.mock_pull_changes.return_value = [
            True,
            {
                self.repository.pk: Locale.objects.filter(
                    pk=self.translated_locale.pk,
                ),
            },
        ]

        sync_translations(
            self.db_project.pk,
            self.project_sync_log.pk,
            self.now,
            no_commit=False,
        )

        assert_false(self.mock_commit_changes.called)

    def test_remove_duplicate_approvals(self):
        """
        Ensure that duplicate approvals are removed.
        """
        # Trigger creation of new approved translation.
        self.main_vcs_translation.strings[None] = 'New Translated String'
        self.main_vcs_translation.fuzzy = False
        self.mock_pull_changes.return_value = [True, {
            self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)
        }]

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

        with patch('pontoon.sync.tasks.VCSProject', return_value=self.vcs_project):
            sync_translations(self.db_project.pk, self.project_sync_log.pk,
                              self.now)

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

    def test_create_repository_log(self):
        assert_false(RepositorySyncLog.objects.exists())

        repo = RepositoryFactory.create()
        self.db_project.repositories = [repo]
        self.db_project.save()
        self.mock_pull_changes.return_value = [True, {
            repo.pk: Locale.objects.filter(pk=self.translated_locale.pk)
        }]

        sync_translations(self.db_project.pk, self.project_sync_log.pk,
                          self.now)

        log = RepositorySyncLog.objects.get(repository=repo.pk)
        assert_equal(log.repository, repo)


class UserError(Exception):
    pass


class SyncExecutionTests(TestCase):
    def test_serial_task(self):
        """
        Test if sync will create lock in cache and release this after task is done.
        """
        @serial_task(100)
        def test_task(self, callback):
            return callback()

        def execute_second_inner_task():
            return test_task.delay(lambda: None)

        first_call = test_task.delay(execute_second_inner_task)
        second_call = first_call.get()

        assert_true(first_call.successful())
        assert_true(second_call.failed())
        assert_raises(RuntimeError, second_call.get)

    def test_release_lock_after_timeout(self):
        """
        Tests if lock is released after specified timeout.
        """
        with patch('pontoon.sync.core.cache') as mock_cache:
            @serial_task(3)
            def timeout_task(self):
                return 42
            first_call = timeout_task.delay()

            assert_true(first_call.successful())
            assert_equal(first_call.get(), 42)
            mock_cache.add.assert_called_with(ANY, ANY, timeout=3)

    def test_parametrized_serial_task(self):
        """
        Serial task should be able to work simultaneously for different parameters.
        """
        with patch('pontoon.sync.core.cache') as mock_cache:
            @serial_task(3, lock_key="param={0}")
            def task_lock_key(self, param):
                return param

            first_call = task_lock_key.delay(42)
            second_call = task_lock_key.delay(24)
            assert_true(first_call.successful())
            assert_true(second_call.successful())
            assert_true(first_call.get(), 42)
            assert_true(second_call.get(), 24)
            mock_cache.add.assert_any_call(CONTAINS('task_lock_key[param=42]'), ANY, timeout=3)
            mock_cache.add.assert_any_call(CONTAINS('task_lock_key[param=24]'), ANY, timeout=3)

    def test_exception_during_sync(self):
        """
        Any error during performing synchronization should release the lock.
        """
        @serial_task(100)
        def exception_task(self):
            raise UserError

        first_call = exception_task.delay()
        second_call = exception_task.delay()

        assert_true(first_call.failed())
        assert_true(second_call.failed())
        assert_raises(UserError, first_call.get)
        assert_raises(UserError, second_call.get)
