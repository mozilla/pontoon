import logging

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from pontoon.base.models import (
    ChangedEntityLocale,
    Project,
    Repository,
    Resource,
)

from pontoon.base.tasks import PontoonTask
from pontoon.sync.changeset import ChangeSet
from pontoon.sync.core import (
    commit_changes,
    pull_changes,
    sync_project as perform_sync_project,
    serial_task,
    update_translated_resources,
    update_translations,
)
from pontoon.sync.models import ProjectSyncLog, RepositorySyncLog, SyncLog
from pontoon.sync.vcs.repositories import CommitToRepositoryException
from pontoon.sync.vcs.models import VCSProject, MissingSourceDirectoryError


log = logging.getLogger(__name__)


def get_or_fail(ModelClass, message=None, **kwargs):
    try:
        return ModelClass.objects.get(**kwargs)
    except ModelClass.DoesNotExist:
        if message is not None:
            log.error(message)
        raise


def sync_project_error(error, *args, **kwargs):
    ProjectSyncLog.objects.create(
        sync_log=SyncLog.objects.get(pk=args[1]),
        project=Project.objects.get(pk=args[0]),
        start_time=timezone.now()
    ).skip()


def sync_project_repo_error(error, *args, **kwargs):
    RepositorySyncLog.objects.create(
        project_sync_log=ProjectSyncLog.objects.get(pk=args[2]),
        repository=Repository.objects.get(pk=args[1]),
        start_time=timezone.now()
    ).end()


def update_locale_project_locale_stats(locale, project):
    locale.aggregate_stats()
    locale.project_locale.get(project=project).aggregate_stats()


@serial_task(settings.SYNC_TASK_TIMEOUT, base=PontoonTask, lock_key='project={0}', on_error=sync_project_error)
def sync_project(self, project_pk, sync_log_pk, locale=None, no_pull=False, no_commit=False, force=False):
    """Fetch the project with the given PK and perform sync on it."""
    db_project = get_or_fail(Project, pk=project_pk,
        message='Could not sync project with pk={0}, not found.'.format(project_pk))
    sync_log = get_or_fail(SyncLog, pk=sync_log_pk,
        message=('Could not sync project {0}, log with pk={1} not found.'
                 .format(db_project.slug, sync_log_pk)))

    log.info('Syncing project {0}.'.format(db_project.slug))

    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    project_sync_log = ProjectSyncLog.objects.create(
        sync_log=sync_log,
        project=db_project,
        start_time=now
    )

    # We have to cache changed files before last revision is overriden by pull
    if no_pull:
        repos_changed = True  # Assume changed.
    else:
        repos_changed, _ = pull_changes(db_project)

    # If the repos haven't changed since the last sync and there are
    # no Pontoon-side changes for this project, quit early.
    if not force and not repos_changed and not db_project.needs_sync:
        log.info('Skipping project {0}, no changes detected.'.format(db_project.slug))
        project_sync_log.skip()
        return

    # Do not sync resources if locale specified
    if locale:
        repo = locale.get_repository(db_project)
        if repo:
            sync_project_repo.delay(
                project_pk,
                repo.pk,
                project_sync_log.pk,
                now,
                locale=locale,
                no_pull=no_pull,
                no_commit=no_commit,
                full_scan=force
            )

    else:
        try:
            obsolete_vcs_entities, obsolete_vcs_resources = perform_sync_project(db_project, now, full_scan=force)
        except MissingSourceDirectoryError, e:
            log.error(e)
            project_sync_log.skip()
            return

        log.info('Synced resources for project {0}.'.format(db_project.slug))

        # No need to sync translations if it's a source repository
        for repo in db_project.repositories.exclude(source_repo=True):
            sync_project_repo.delay(
                project_pk,
                repo.pk,
                project_sync_log.pk,
                now,
                obsolete_vcs_entities,
                obsolete_vcs_resources,
                no_pull=no_pull,
                no_commit=no_commit,
                full_scan=force
            )

        for repo in db_project.repositories.filter(source_repo=True):
            repo.set_current_last_synced_revisions()


@serial_task(settings.SYNC_TASK_TIMEOUT, base=PontoonTask, lock_key='project={0},repo={1}', on_error=sync_project_repo_error)
def sync_project_repo(self, project_pk, repo_pk, project_sync_log_pk, now, obsolete_vcs_entities=None,
                      obsolete_vcs_resources=None, locale=None, no_pull=False, no_commit=False,
                      full_scan=False):
    db_project = get_or_fail(Project, pk=project_pk,
        message='Could not sync project with pk={0}, not found.'.format(project_pk))
    repo = get_or_fail(Repository, pk=repo_pk,
        message='Could not sync repo with pk={0}, not found.'.format(repo_pk))
    project_sync_log = get_or_fail(ProjectSyncLog, pk=project_sync_log_pk,
        message=('Could not sync project {0}, log with pk={1} not found.'
                 .format(db_project.slug, project_sync_log_pk)))
    log.info('Syncing repo: {}'.format(repo.url))

    repo_sync_log = RepositorySyncLog.objects.create(
        project_sync_log=project_sync_log,
        repository=repo,
        start_time=timezone.now()
    )

    # Pull VCS changes in case we're on a different worker than the one
    # sync started on.
    if not no_pull:
        pull_changes(db_project)

    if locale:
        locales = [locale]
    else:
        locales = repo.locales

    # Cannot skip earlier - repo.locales is only available after pull_changes()
    if not locales:
        log.debug('Skipping repo `{0}` for project {1}, no locales to sync found within.'
                  .format(repo.url, db_project.slug))
        repo_sync_log.end()
        return

    vcs_project = VCSProject(
        db_project,
        locales=locales,
        obsolete_entities_paths=Resource.objects.obsolete_entities_paths(obsolete_vcs_entities),
        full_scan=full_scan
    )

    for locale in locales:
        try:
            with transaction.atomic():
                # Skip locales that have nothing to sync
                if vcs_project.synced_locales and locale not in vcs_project.synced_locales:
                    if obsolete_vcs_entities or obsolete_vcs_resources:
                        update_locale_project_locale_stats(locale, db_project)
                    continue

                changeset = ChangeSet(db_project, vcs_project, now, obsolete_vcs_entities, obsolete_vcs_resources)
                update_translations(db_project, vcs_project, locale, changeset)
                changeset.execute()

                update_translated_resources(db_project, vcs_project, changeset, locale)

                # Skip if none of the locales has anything to sync
                # VCSProject.synced_locales is set on a first call to
                # VCSProject.resources, which is set in
                # pontoon.sync.core.update_translated_resources()
                if len(vcs_project.synced_locales) == 0:
                    if obsolete_vcs_entities or obsolete_vcs_resources:
                        for l in locales:
                            update_locale_project_locale_stats(l, db_project)
                        db_project.aggregate_stats()

                    log.info('Skipping repo `{0}` for project {1}, none of the locales has anything to sync.'
                             .format(repo.url, db_project.slug))
                    repo_sync_log.end()
                    return

                update_locale_project_locale_stats(locale, db_project)

                # Clear out the "has_changed" markers now that we've finished
                # syncing.
                (ChangedEntityLocale.objects
                    .filter(entity__resource__project=db_project,
                            locale=locale,
                            when__lte=now)
                    .delete())

                # Clean up any duplicate approvals at the end of sync right
                # before we commit the transaction to avoid race conditions.
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE base_translation AS b
                        SET approved = FALSE, approved_date = NULL
                        WHERE
                          id IN
                            (SELECT trans.id FROM base_translation AS trans
                             LEFT JOIN base_entity AS ent ON ent.id = trans.entity_id
                             LEFT JOIN base_resource AS res ON res.id = ent.resource_id
                             WHERE locale_id = %(locale_id)s
                               AND res.project_id = %(project_id)s)
                          AND approved_date !=
                            (SELECT max(approved_date)
                             FROM base_translation
                             WHERE entity_id = b.entity_id
                               AND locale_id = b.locale_id
                               AND (plural_form = b.plural_form OR plural_form IS NULL));
                    """, {
                        'locale_id': locale.id,
                        'project_id': db_project.id
                    })

                # Perform the commit last so that, if it succeeds, there is
                # nothing after it to fail.
                if not no_commit and locale in changeset.locales_to_commit:
                    commit_changes(db_project, vcs_project, changeset, locale)

        except CommitToRepositoryException as err:
            # Transaction aborted, log and move on to the next locale.
            log.warning(
                'Failed to sync locale {locale} for project {project} due to '
                'commit error: {error}'.format(
                    locale=locale.code,
                    project=db_project.slug,
                    error=err,
                )
            )

    with transaction.atomic():
        db_project.aggregate_stats()

    log.info('Synced translations for project {0} in locales {1}.'.format(
        db_project.slug, ','.join(locale.code for locale in vcs_project.synced_locales)
    ))
    repo_sync_log.end()
