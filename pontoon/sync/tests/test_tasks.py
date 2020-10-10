from __future__ import absolute_import

import pytest
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

        self.mock_pull_source_repo_changes = self.patch(
            "pontoon.sync.tasks.pull_source_repo_changes", return_value=True
        )
        self.mock_project_needs_sync = self.patch_object(
            Project, "needs_sync", new_callable=PropertyMock, return_value=True
        )

        self.mock_sync_translations = self.patch("pontoon.sync.tasks.sync_translations")

        self.mock_update_originals = self.patch(
            "pontoon.sync.tasks.update_originals", return_value=[[], [], [], []]
        )

        self.mock_source_directory_path = self.patch(
            "pontoon.sync.vcs.models.VCSProject.source_directory_path",
            return_value=self.repository.checkout_path,
        )

    def test_missing_project(self):
        """
        If a project with the given PK doesn't exist, log it and exit.
        """
        with patch("pontoon.sync.tasks.log") as mock_log:
            with pytest.raises(Project.DoesNotExist):
                sync_project(99999, self.sync_log.pk)
            mock_log.error.assert_called_with(CONTAINS("99999"))
            assert not self.mock_update_originals.called

    def test_missing_log(self):
        """
        If a log with the given PK doesn't exist, log it and exit.
        """
        with patch("pontoon.sync.tasks.log") as mock_log:
            with pytest.raises(SyncLog.DoesNotExist):
                sync_project(self.db_project.pk, 99999)
            mock_log.error.assert_called_with(CONTAINS("99999"))
            assert not self.mock_update_originals.called

    def test_db_changed_no_repo_changed(self):
        """
        If the database has changes and VCS doesn't, skip syncing
        resources, but sync translations.
        """
        self.mock_pull_source_repo_changes.return_value = False
        self.mock_project_needs_sync.return_value = True

        with patch("pontoon.sync.tasks.log") as mock_log:
            sync_project(self.db_project.pk, self.sync_log.pk)

        sync_project(self.db_project.pk, self.sync_log.pk)
        assert not self.mock_update_originals.called
        mock_log.info.assert_called_with(
            CONTAINS("Skipping syncing sources", self.db_project.slug)
        )

    def test_no_changes_skip(self):
        """
        If the database and the source repository both have no
        changes, and project has a single repository, skip sync.
        """
        self.mock_pull_source_repo_changes.return_value = False
        self.mock_project_needs_sync.return_value = False

        with patch("pontoon.sync.tasks.log") as mock_log:
            sync_project(self.db_project.pk, self.sync_log.pk)

        assert not self.mock_update_originals.called
        mock_log.info.assert_called_with(
            CONTAINS("Skipping project", self.db_project.slug)
        )

        # When skipping, mark the project log properly.
        assert ProjectSyncLog.objects.get(project=self.db_project).skipped

    def test_no_changes_force(self):
        """
        If the database and VCS both have no changes, but force is true,
        do not skip syncing resources.
        """
        self.mock_pull_source_repo_changes.return_value = False
        self.mock_project_needs_sync.return_value = False

        sync_project(self.db_project.pk, self.sync_log.pk, force=True)
        assert self.mock_update_originals.called

    def test_no_pull(self):
        """
        Don't call repo.pull if command.no_pull is True.
        """
        sync_project(self.db_project.pk, self.sync_log.pk, no_pull=True)
        assert not self.mock_pull_source_repo_changes.called

    def test_create_project_log(self):
        assert not ProjectSyncLog.objects.exists()
        sync_project(self.db_project.pk, self.sync_log.pk)

        log = ProjectSyncLog.objects.get(project=self.db_project)
        assert self.mock_sync_translations.call_args[0][1].pk == log.pk


class SyncTranslationsTests(FakeCheckoutTestCase):
    def setUp(self):
        super(SyncTranslationsTests, self).setUp()
        self.project_sync_log = ProjectSyncLogFactory.create()

        self.mock_pull_locale_repo_changes = self.patch(
            "pontoon.sync.tasks.pull_locale_repo_changes", return_value=[True, {}]
        )
        self.mock_commit_changes = self.patch("pontoon.sync.tasks.commit_changes")
        self.mock_pretranslate = self.patch("pontoon.sync.tasks.pretranslate")
        self.mock_repo_checkout_path = self.patch_object(
            Repository,
            "checkout_path",
            new_callable=PropertyMock,
            return_value=FAKE_CHECKOUT_PATH,
        )

    def test_clear_changed_entities(self):
        """
        Delete all ChangedEntityLocale objects for the project created
        before the sync started after handling it.
        """
        self.now = aware_datetime(1970, 1, 2)
        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)},
        ]

        changed1, changed2, changed_after = ChangedEntityLocaleFactory.create_batch(
            3,
            locale=self.translated_locale,
            entity__resource=self.main_db_resource,
            when=aware_datetime(1970, 1, 1),
        )
        changed_after.when = aware_datetime(1970, 1, 3)
        changed_after.save()

        sync_translations(self.db_project, self.project_sync_log, self.now, True)
        with pytest.raises(ChangedEntityLocale.DoesNotExist):
            changed1.refresh_from_db()
        with pytest.raises(ChangedEntityLocale.DoesNotExist):
            changed2.refresh_from_db()
        changed_after.refresh_from_db()  # Should not raise

    def test_no_commit(self):
        """Don't call commit_changes if command.no_commit is True."""
        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)},
        ]
        sync_translations(
            self.db_project, self.project_sync_log, self.now, True, no_commit=True
        )
        assert not self.mock_commit_changes.called

    def test_readonly_locales(self):
        """Don't call commit_changes for locales in read-only mode."""
        project_locale = self.translated_locale.project_locale.get(
            project=self.db_project,
        )
        project_locale.readonly = True
        project_locale.save()

        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk,)},
        ]

        sync_translations(
            self.db_project, self.project_sync_log, self.now, True, no_commit=False,
        )

        assert not self.mock_commit_changes.called

    def test_remove_duplicate_approvals(self):
        """
        Ensure that duplicate approvals are removed.
        """
        # Trigger creation of new approved translation.
        self.main_vcs_translation.strings[None] = "New Translated String"
        self.main_vcs_translation.fuzzy = False
        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)},
        ]

        # Translation approved after the sync started simulates the race
        # where duplicate translations occur.
        duplicate_translation = TranslationFactory.create(
            entity=self.main_db_entity,
            locale=self.translated_locale,
            string="Other New Translated String",
            approved=True,
            approved_date=aware_datetime(1970, 1, 3),
        )
        ChangedEntityLocale.objects.filter(entity=self.main_db_entity).delete()

        with patch("pontoon.sync.tasks.VCSProject", return_value=self.vcs_project):
            sync_translations(self.db_project, self.project_sync_log, self.now, True)

        # Only one translation should be approved: the duplicate_translation.
        assert self.main_db_entity.translation_set.filter(approved=True).count() == 1
        new_translation = self.main_db_entity.translation_set.get(
            string="New Translated String"
        )
        assert not new_translation.approved
        assert new_translation.approved_date is None

        duplicate_translation.refresh_from_db()
        assert duplicate_translation.approved
        assert duplicate_translation.approved_date == aware_datetime(1970, 1, 3)

    def test_create_repository_log(self):
        assert not RepositorySyncLog.objects.exists()

        repo = RepositoryFactory.create()
        self.db_project.repositories.set([repo])
        self.db_project.save()
        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {repo.pk: Locale.objects.filter(pk=self.translated_locale.pk)},
        ]

        sync_translations(self.db_project, self.project_sync_log, self.now, True)

        log = RepositorySyncLog.objects.get(repository=repo.pk)
        assert log.repository == repo

    def test_no_pretranslation(self):
        """
        Ensure that pretranslation isn't called if pretranslation not enabled
        or no new Entity, Locale or TranslatedResource is created.
        """
        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)},
        ]

        sync_translations(
            self.db_project,
            self.project_sync_log,
            self.now,
            True,
            [],
            [],
            [],
            ["new_entity"],
        )

        # Pretranslation is not enabled
        assert not self.mock_pretranslate.called

        self.db_project.pretranslation_enabled = True
        self.db_project.save()

        with self.patch(
            "pontoon.sync.tasks.update_translated_resources", return_value=False
        ):
            sync_translations(self.db_project, self.project_sync_log, self.now, True)

        # No new Entity, Locale or TranslatedResource
        assert not self.mock_pretranslate.called

    def test_new_entities_pretranslation(self):
        """
        Test if pretranslation is called for newly added entities.
        """
        self.db_project.pretranslation_enabled = True
        self.db_project.save()
        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)},
        ]
        all_locales = list(self.db_project.locales.values_list("pk", flat=True))

        with self.patch(
            "pontoon.sync.tasks.update_translated_resources", return_value=False
        ):
            sync_translations(
                self.db_project,
                self.project_sync_log,
                self.now,
                True,
                [],
                [],
                [],
                ["new_entity"],
            )

        assert self.mock_pretranslate.called
        assert self.mock_pretranslate.call_args[1]["entities"] == ["new_entity"]
        assert list(self.mock_pretranslate.call_args[1]["locales"]) == all_locales

    def test_new_translated_resource_pretranslation(self):
        """
        Test if pretranslation is called for locales with newly added TranslatedResource.
        """
        self.db_project.pretranslation_enabled = True
        self.db_project.save()
        self.mock_pull_locale_repo_changes.return_value = [
            True,
            {self.repository.pk: Locale.objects.filter(pk=self.translated_locale.pk)},
        ]

        sync_translations(
            self.db_project,
            self.project_sync_log,
            self.now,
            True,
            [],
            [],
            [],
            ["new_entity"],
        )

        assert self.mock_pretranslate.called
        assert self.mock_pretranslate.call_args[1]["locales"] == [
            self.translated_locale.pk
        ]

        # Ensure that pretranslate is called only once for the locale.
        assert self.mock_pretranslate.call_args[1].get("entities") is None


class UserError(Exception):
    pass


class SyncExecutionTests(TestCase):
    def test_serial_task(self):
        """
        Test if sync will create lock in cache and release this after task is done.
        """

        @serial_task(100)
        def test_task(self, call_subtask):
            if call_subtask:
                return subtask()

        def subtask():
            return test_task.delay()

        first_call = test_task.delay(call_subtask=True)
        second_call = first_call.get()

        assert first_call.successful()
        assert second_call.failed()
        with pytest.raises(RuntimeError):
            second_call.get()

    def test_release_lock_after_timeout(self):
        """
        Tests if lock is released after specified timeout.
        """
        with patch("pontoon.sync.core.cache") as mock_cache:

            @serial_task(3)
            def timeout_task(self):
                return 42

            first_call = timeout_task.delay()

            assert first_call.successful()
            assert first_call.get(), 42
            mock_cache.add.assert_called_with(ANY, ANY, timeout=3)

    def test_parametrized_serial_task(self):
        """
        Serial task should be able to work simultaneously for different parameters.
        """
        with patch("pontoon.sync.core.cache") as mock_cache:

            @serial_task(3, lock_key="param={0}")
            def task_lock_key(self, param):
                return param

            first_call = task_lock_key.delay(42)
            second_call = task_lock_key.delay(24)
            assert first_call.successful()
            assert second_call.successful()
            assert first_call.get() == 42
            assert second_call.get() == 24
            mock_cache.add.assert_any_call(
                CONTAINS("task_lock_key[param=42]"), ANY, timeout=3
            )
            mock_cache.add.assert_any_call(
                CONTAINS("task_lock_key[param=24]"), ANY, timeout=3
            )

    def test_exception_during_sync(self):
        """
        Any error during performing synchronization should release the lock.
        """

        @serial_task(100)
        def exception_task(self):
            raise UserError

        first_call = exception_task.delay()
        second_call = exception_task.delay()

        assert first_call.failed()
        assert second_call.failed()
        with pytest.raises(UserError):
            first_call.get()
        with pytest.raises(UserError):
            second_call.get()
