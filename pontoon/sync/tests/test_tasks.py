from django_nose.tools import assert_equal, assert_false, assert_raises, assert_true
from mock import patch, PropertyMock
from waiting import wait
from django.core.cache import cache

from pontoon.base.models import ChangedEntityLocale, Project, Repository
from pontoon.base.tests import (
    ChangedEntityLocaleFactory,
    CONTAINS,
    ProjectFactory,
    TestCase,
    TranslationFactory,
)
from pontoon.base.utils import aware_datetime
from pontoon.sync.core import serial_task
from pontoon.sync.tasks import sync_project, sync_project_repo
from pontoon.sync.tests import FAKE_CHECKOUT_PATH, FakeCheckoutTestCase



class SyncProjectTests(TestCase):
    def setUp(self):
        super(SyncProjectTests, self).setUp()
        self.db_project = ProjectFactory.create()

        self.mock_pull_changes = self.patch(
            'pontoon.sync.tasks.pull_changes', return_value=True)
        self.mock_project_needs_sync = self.patch_object(
            Project, 'needs_sync', new_callable=PropertyMock, return_value=True)
        self.mock_sync_project_repo = self.patch('pontoon.sync.tasks.sync_project_repo')

        self.mock_perform_sync_project = self.patch('pontoon.sync.tasks.perform_sync_project')

    def test_missing_project(self):
        """
        If a project with the given PK doesn't exist, log it and exit.
        """
        with patch('pontoon.sync.tasks.log') as mock_log:
            sync_project(99999)
            mock_log.error.assert_called_with(CONTAINS('99999'))
            assert_false(self.mock_perform_sync_project.called)

    def test_db_changed_no_repo_changed(self):
        """
        If the database has changes and VCS doesn't, do not skip syncing
        the project.
        """
        self.mock_pull_changes.return_value = False
        self.mock_project_needs_sync.return_value = True

        sync_project(self.db_project.pk)
        assert_true(self.mock_perform_sync_project.called)

    def test_no_changes_skip(self):
        """
        If the database and VCS both have no changes, skip sync and log
        a message.
        """
        self.mock_pull_changes.return_value = False
        self.mock_project_needs_sync.return_value = False

        with patch('pontoon.sync.tasks.log') as mock_log:
            sync_project(self.db_project.pk)

        assert_false(self.mock_perform_sync_project.called)
        mock_log.info.assert_called_with(
            CONTAINS('Skipping', self.db_project.slug)
        )

    def test_no_changes_force(self):
        """
        If the database and VCS both have no changes, but force is true,
        do not skip sync.
        """
        self.mock_pull_changes.return_value = False
        self.mock_project_needs_sync.return_value = False

        sync_project(self.db_project.pk, force=True)
        assert_true(self.mock_perform_sync_project.called)

    def test_no_pull(self):
        """
        Don't call repo.pull if command.no_pull is True.
        """
        sync_project(self.db_project.pk, no_pull=True)
        assert_false(self.mock_pull_changes.called)


class SyncProjectRepoTests(FakeCheckoutTestCase):
    def setUp(self):
        super(SyncProjectRepoTests, self).setUp()
        self.mock_pull_changes = self.patch(
            'pontoon.sync.tasks.pull_changes', return_value=True)
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
        changed1, changed2, changed_after = ChangedEntityLocaleFactory.create_batch(3,
            locale=self.translated_locale,
            entity__resource=self.main_db_resource,
            when=aware_datetime(1970, 1, 1)
        )
        changed_after.when = aware_datetime(1970, 1, 3)
        changed_after.save()

        sync_project_repo(self.db_project.pk, self.repository.pk, self.now)
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed1.refresh_from_db()
        with assert_raises(ChangedEntityLocale.DoesNotExist):
            changed2.refresh_from_db()
        changed_after.refresh_from_db()  # Should not raise

    def test_reset_project_has_changed(self):
        """After syncing, set db_project.has_changed to False."""
        self.db_project.has_changed = True
        self.db_project.save()

        sync_project(self.db_project.pk)
        self.db_project.refresh_from_db()
        assert_false(self.db_project.has_changed)

    def test_no_commit(self):
        """Don't call commit_changes if command.no_commit is True."""
        sync_project_repo(self.db_project.pk, self.repository.pk, self.now,
                          no_commit=True)
        assert_false(self.mock_commit_changes.called)

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

        with patch('pontoon.sync.tasks.VCSProject', return_value=self.vcs_project):
            sync_project_repo(self.db_project.pk, self.repository.pk, self.now)

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


class UserError(Exception):
    pass

class SyncExecutionTests(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()

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
        @serial_task(3)
        def timeout_task(self):
            return wait(lambda: not cache.get('serial_task.pontoon.sync.tests.test_tasks.timeout_task'),
                timeout_seconds=10)

        first_call = timeout_task.delay()
        assert_false(cache.get('serial_task.pontoon.sync.tests.test_tasks.timeout_task'))
        assert_true(first_call.successful())
        assert_true(first_call.get())

        # Test if we can execute second call after previous one was released
        second_call = timeout_task.delay()
        assert_false(cache.get('serial_task.pontoon.sync.tests.test_tasks.timeout_task'))
        assert_true(second_call.successful())
        assert_true(second_call.get())

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
