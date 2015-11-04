import logging

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from celery import shared_task

from pontoon.administration.vcs import CommitToRepositoryException
from pontoon.base.models import ChangedEntityLocale, Project, Repository
from pontoon.base.tasks import PontoonTask
from pontoon.sync.changeset import ChangeSet
from pontoon.sync.core import (
    commit_changes,
    pull_changes,
    sync_project as perform_sync_project,
    update_project_stats,
    update_translations,
    serial_task
)
from pontoon.sync.vcs_models import VCSProject


log = logging.getLogger(__name__)


@serial_task(settings.SYNC_TASK_TIMEOUT, base=PontoonTask)
def sync_project(self, project_pk, no_pull=False, no_commit=False, force=False):
    """Fetch the project with the given PK and perform sync on it."""
    try:
        db_project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        log.error('Could not sync project with pk={0}, not found.'.format(project_pk))
        return

    log.info('Syncing project {0}.'.format(db_project.slug))

    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    if not no_pull:
        repos_changed = pull_changes(db_project)
    else:
        repos_changed = True  # Assume changed.

    # If the repos haven't changed since the last sync and there are
    # no Pontoon-side changes for this project, quit early.
    if not force and not repos_changed and not db_project.needs_sync:
        log.info('Skipping project {0}, no changes detected.'.format(db_project.slug))
        return

    perform_sync_project(db_project, now)
    for repo in db_project.repositories.all():
        sync_project_repo.delay(project_pk, repo.pk, now, no_pull=no_pull, no_commit=no_commit)

    log.info('Synced resources for project {0}.'.format(db_project.slug))


@shared_task(base=PontoonTask)
def sync_project_repo(project_pk, repo_pk, now, no_pull=False, no_commit=False):
    try:
        db_project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        log.error('Could not sync project with pk={0}, not found.'.format(project_pk))
        return

    try:
        repo = Repository.objects.get(pk=repo_pk)
    except Repository.DoesNotExist:
        log.error('Could not sync repo with pk={0}, not found.'.format(repo_pk))
        return

    # Pull VCS changes in case we're on a different worker than the one
    # sync started on.
    if not no_pull:
        pull_changes(db_project)

    if len(repo.locales) < 1:
        log.warning('Could not sync repo `{0}`, no locales found within.'
                    .format(repo.url))
        return

    vcs_project = VCSProject(db_project, locales=repo.locales)
    for locale in repo.locales:
        try:
            with transaction.atomic():
                changeset = ChangeSet(db_project, vcs_project, now)
                update_translations(db_project, vcs_project, locale, changeset)
                changeset.execute()

                update_project_stats(db_project, vcs_project, changeset, locale)

                # Clear out the "has_changed" markers now that we've finished
                # syncing.
                (ChangedEntityLocale.objects
                    .filter(entity__resource__project=db_project,
                            locale=locale,
                            when__lte=now)
                    .delete())
                db_project.has_changed = False
                db_project.save()

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

    log.info('Synced translations for project {0} in locales {1}.'.format(
        db_project.slug, ','.join(locale.code for locale in repo.locales)
    ))
