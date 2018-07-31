import logging

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Q
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
    serial_task,
    update_originals,
    update_translated_resources,
    update_translated_resources_no_files,
    update_translations,
    get_changed_locales,
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


def sync_translations_error(error, *args, **kwargs):
    project_sync_log = ProjectSyncLog.objects.get(pk=args[1])
    repository = project_sync_log.project.translation_repositories()[0]

    RepositorySyncLog.objects.create(
        project_sync_log=project_sync_log,
        repository=repository,
        start_time=timezone.now()
    ).end()


def update_locale_project_locale_stats(locale, project):
    locale.aggregate_stats()
    locale.project_locale.get(project=project).aggregate_stats()


@serial_task(
    settings.SYNC_TASK_TIMEOUT,
    base=PontoonTask,
    lock_key='project={0}',
    on_error=sync_project_error
)
def sync_project(
    self, project_pk, sync_log_pk, locale=None, no_pull=False, no_commit=False, force=False
):
    """Fetch the project with the given PK and perform sync on it."""
    db_project = get_or_fail(
        Project,
        pk=project_pk,
        message='Could not sync project with pk={0}, not found.'.format(project_pk)
    )

    sync_log = get_or_fail(
        SyncLog,
        pk=sync_log_pk,
        message=(
            'Could not sync project {0}, log with pk={1} not found.'
            .format(db_project.slug, sync_log_pk)
        )
    )

    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    project_sync_log = ProjectSyncLog.objects.create(
        sync_log=sync_log,
        project=db_project,
        start_time=now
    )

    log.info('Syncing project {0}.'.format(db_project.slug))

    # Sync source strings. We cannot sync sources if locale is specified,
    # because that would apply any source string changes to the specified locale only.
    if locale:
        source_changes = {}
    else:
        source_changes = sync_sources(db_project, now, force, no_pull)
        # Skip syncing translations if we already know there's nothing to sync
        if not source_changes:
            project_sync_log.skip()
            return

    # Sync translations
    sync_translations.delay(
        project_pk,
        project_sync_log.pk,
        now,
        source_changes.get('project_changes'),
        source_changes.get('obsolete_vcs_resources'),
        source_changes.get('new_paths'),
        locale=locale,
        no_pull=no_pull,
        no_commit=no_commit,
        full_scan=force
    )


def sync_sources(db_project, now, force, no_pull):
    # Pull source repository
    if no_pull:
        source_repo_changed = True  # Assume changed
    else:
        source_repo_changed, _ = pull_changes(db_project)

    # If the only repo hasn't changed since the last sync and there are
    # no Pontoon-side changes for this project, quit early.
    if (
        not force and
        not db_project.needs_sync and
        not source_repo_changed and
        db_project.has_single_repo
    ):
        log.info('Skipping project {0}, no changes detected.'.format(db_project.slug))
        return False

    if force or source_repo_changed:
        try:
            project_changes, obsolete_vcs_resources, new_paths = update_originals(
                db_project, now, full_scan=force
            )
        except MissingSourceDirectoryError as e:
            log.error(e)
            return False

        if not db_project.has_single_repo:
            db_project.source_repository.set_last_synced_revisions()
        log.info('Synced sources for project {0}.'.format(db_project.slug))

    else:
        project_changes, obsolete_vcs_resources, new_paths = None, None, None
        log.info(
            'Skipping syncing sources for project {0}, no changes detected.'.format(
                db_project.slug
            )
        )

    return {
        'project_changes': project_changes,
        'obsolete_vcs_resources': obsolete_vcs_resources,
        'new_paths': new_paths,
    }


@serial_task(
    settings.SYNC_TASK_TIMEOUT,
    base=PontoonTask,
    lock_key='project={0},translations',
    on_error=sync_translations_error
)
def sync_translations(
    self, project_pk, project_sync_log_pk, now, project_changes=None, obsolete_vcs_resources=None,
    new_paths=None, locale=None, no_pull=False, no_commit=False, full_scan=False
):
    db_project = get_or_fail(
        Project,
        pk=project_pk,
        message='Could not sync project with pk={0}, not found.'.format(project_pk)
    )

    repos = db_project.translation_repositories()
    repo_pk = repos[0].pk
    repo = get_or_fail(
        Repository,
        pk=repo_pk,
        message='Could not sync repo with pk={0}, not found.'.format(repo_pk)
    )

    project_sync_log = get_or_fail(
        ProjectSyncLog,
        pk=project_sync_log_pk,
        message=(
            'Could not sync project {0}, log with pk={1} not found.'
            .format(db_project.slug, project_sync_log_pk)
        )
    )

    log.info('Syncing translations for project: {}'.format(db_project.slug))

    repo_sync_log = RepositorySyncLog.objects.create(
        project_sync_log=project_sync_log,
        repository=repo,
        start_time=timezone.now()
    )

    if locale:
        locales = db_project.locales.filter(pk=locale.pk)
    else:
        locales = db_project.locales.all()

    if not locales:
        log.info('Skipping syncing translations for project {0}, no locales to sync found within.'
                 .format(db_project.slug))
        repo_sync_log.end()
        return

    # If project repositories have API access, we can retrieve latest commit hashes and detect
    # changed locales before the expensive VCS pull/clone operations. When performing full scan,
    # we still need to sync all locales.
    if not full_scan:
        locales = get_changed_locales(db_project, locales, now)

    # Pull VCS changes in case we're on a different worker than the one
    # sync started on.
    if not no_pull:
        log.info('Pulling changes for project {0} started.'.format(db_project.slug))
        repos_changed, repo_locales = pull_changes(db_project, locales)
        repos = repos.filter(pk__in=repo_locales.keys())
        log.info('Pulling changes for project {0} complete.'.format(db_project.slug))

    changed_resources = []
    obsolete_vcs_entities = []

    if project_changes:
        updated_entity_pks = []
        for locale_code, db_entity, vcs_entity in project_changes['update_db']:
            updated_entity_pks.append(db_entity.pk)

        obsolete_entity_pks = project_changes['obsolete_db']
        changed_resources = db_project.resources.filter(
            Q(entities__date_created=now) |
            Q(entities__pk__in=updated_entity_pks + obsolete_entity_pks)
        ).distinct()

        obsolete_vcs_entities = project_changes['obsolete_db']

    # If none of the repos has changed since the last sync and there are
    # no Pontoon-side changes for this project, quit early.
    if (
        not full_scan and
        not db_project.needs_sync and
        not repos_changed and
        not (changed_resources or obsolete_vcs_resources)
    ):
        log.info('Skipping project {0}, no changes detected.'.format(db_project.slug))
        repo_sync_log.end()
        return

    obsolete_entities_paths = (
        Resource.objects.obsolete_entities_paths(obsolete_vcs_entities) if obsolete_vcs_entities
        else None
    )

    vcs_project = VCSProject(
        db_project,
        now,
        locales=locales,
        repo_locales=repo_locales,
        obsolete_entities_paths=obsolete_entities_paths,
        new_paths=new_paths,
        full_scan=full_scan
    )

    synced_locales = set()
    failed_locales = set()
    readonly_locales = db_project.locales.filter(project_locale__readonly=True)

    for locale in locales:
        try:
            with transaction.atomic():
                # Sets VCSProject.synced_locales, needed to skip early
                if not vcs_project.synced_locales:
                    vcs_project.resources

                # Skip all locales if none of the them has anything to sync
                if len(vcs_project.synced_locales) == 0:
                    break

                # Skip locales that have nothing to sync
                if vcs_project.synced_locales and locale not in vcs_project.synced_locales:
                    continue

                changeset = ChangeSet(db_project, vcs_project, now, locale)
                update_translations(db_project, vcs_project, locale, changeset)
                changeset.execute()
                update_translated_resources(db_project, vcs_project, locale)
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
                if (
                    not no_commit and
                    locale in changeset.locales_to_commit and
                    locale not in readonly_locales
                ):
                    commit_changes(db_project, vcs_project, changeset, locale)

                log.info(
                    'Synced locale {locale} for project {project}.'.format(
                        locale=locale.code,
                        project=db_project.slug,
                    )
                )

                synced_locales.add(locale.code)

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

            failed_locales.add(locale.code)

    # If sources have changed, update stats for all locales.
    if changed_resources or obsolete_vcs_resources:
        for locale in db_project.locales.all():
            # Already synced.
            if locale.code in synced_locales:
                continue

            # We have files: update all translated resources.
            if locale in locales:
                update_translated_resources(db_project, vcs_project, locale)

            # We don't have files: we can still update asymmetric translated resources.
            else:
                update_translated_resources_no_files(db_project, locale, changed_resources)

            update_locale_project_locale_stats(locale, db_project)
            synced_locales.add(locale.code)

            log.info(
                'Synced source changes for locale {locale} for project {project}.'.format(
                    locale=locale.code,
                    project=db_project.slug,
                )
            )

        db_project.aggregate_stats()

    if synced_locales:
        log.info('Synced translations for project {0} in locales {1}.'.format(
            db_project.slug, ','.join(synced_locales)
        ))
    elif failed_locales:
        log.info('Failed to sync translations for project {0} due to commit error.'.format(
            db_project.slug
        ))
    else:
        log.info(
            'Skipping syncing translations for project {0}, none of the locales '
            'has anything to sync.'.format(db_project.slug)
        )

    for r in repos:
        r.set_last_synced_revisions(
            locales=repo_locales[r.pk].exclude(code__in=failed_locales)
        )
    repo_sync_log.end()
