import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from pontoon.base.models import (
    ChangedEntityLocale,
    Project,
    Locale,
)

from pontoon.base.tasks import PontoonTask
from pontoon.sync.changeset import ChangeSet
from pontoon.sync.core import (
    commit_changes,
    pull_source_repo_changes,
    pull_locale_repo_changes,
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
from pontoon.pretranslation.tasks import pretranslate


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
        start_time=timezone.now(),
    ).skip()


def update_locale_project_locale_stats(locale, project):
    locale.aggregate_stats()
    locale.project_locale.get(project=project).aggregate_stats()


@serial_task(
    settings.SYNC_TASK_TIMEOUT,
    base=PontoonTask,
    lock_key="project={0}",
    on_error=sync_project_error,
)
def sync_project(
    self, project_pk, sync_log_pk, no_pull=False, no_commit=False, force=False,
):
    """Fetch the project with the given PK and perform sync on it."""
    db_project = get_or_fail(
        Project,
        pk=project_pk,
        message="Could not sync project with pk={0}, not found.".format(project_pk),
    )

    sync_log = get_or_fail(
        SyncLog,
        pk=sync_log_pk,
        message=(
            "Could not sync project {0}, log with pk={1} not found.".format(
                db_project.slug, sync_log_pk
            )
        ),
    )

    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    project_sync_log = ProjectSyncLog.objects.create(
        sync_log=sync_log, project=db_project, start_time=now
    )

    log.info("Syncing project {0}.".format(db_project.slug))

    source_changes = sync_sources(db_project, now, force, no_pull)
    # Skip syncing translations if we already know there's nothing to sync
    # or if no source directory found.
    if not source_changes:
        project_sync_log.skip()
        return

    # Sync translations
    sync_translations(
        db_project,
        project_sync_log,
        now,
        source_changes.get("has_source_repo_changed"),
        source_changes.get("added_paths"),
        source_changes.get("removed_paths"),
        source_changes.get("changed_paths"),
        source_changes.get("new_entities"),
        no_pull=no_pull,
        no_commit=no_commit,
        force=force,
    )


def sync_sources(db_project, now, force, no_pull):
    # Pull from source repository
    if no_pull:
        has_source_repo_changed = True
    else:
        log.info(
            "Pulling source changes for project {0} started.".format(db_project.slug)
        )
        has_source_repo_changed = pull_source_repo_changes(db_project)
        log.info(
            "Pulling source changes for project {0} complete.".format(db_project.slug)
        )

    # If the only repo hasn't changed since the last sync and there are
    # no Pontoon-side changes for this project, quit early.
    if (
        not force
        and not db_project.needs_sync
        and not has_source_repo_changed
        and db_project.has_single_repo
    ):
        log.info("Skipping project {0}, no changes detected.".format(db_project.slug))
        return False

    if force or has_source_repo_changed:
        try:
            added_paths, removed_paths, changed_paths, new_entities = update_originals(
                db_project, now, force=force
            )
        except MissingSourceDirectoryError as e:
            log.error(e)
            return False

        log.info("Synced sources for project {0}.".format(db_project.slug))

    else:
        added_paths, removed_paths, changed_paths, new_entities = None, None, None, None
        log.info(
            "Skipping syncing sources for project {0}, no changes detected.".format(
                db_project.slug
            )
        )

    return {
        "has_source_repo_changed": has_source_repo_changed,
        "added_paths": added_paths,
        "removed_paths": removed_paths,
        "changed_paths": changed_paths,
        "new_entities": new_entities,
    }


def sync_translations(
    db_project,
    project_sync_log,
    now,
    has_source_repo_changed,
    added_paths=None,
    removed_paths=None,
    changed_paths=None,
    new_entities=None,
    no_pull=False,
    no_commit=False,
    force=False,
):
    repo = db_project.translation_repositories()[0]

    log.info("Syncing translations for project: {}".format(db_project.slug))

    repo_sync_log = RepositorySyncLog.objects.create(
        project_sync_log=project_sync_log, repository=repo, start_time=timezone.now()
    )

    locales = db_project.locales.all()

    if not locales:
        log.info(
            "Skipping syncing translations for project {0}, no locales to sync "
            "found within.".format(db_project.slug)
        )
        repo_sync_log.end()
        return

    # If project repositories have API access, we can retrieve latest commit hashes and detect
    # changed locales before the expensive VCS pull/clone operations. When performing full scan,
    # we still need to sync all locales.
    if not force:
        locales = get_changed_locales(db_project, locales, now)

    readonly_locales = db_project.locales.filter(project_locale__readonly=True)
    added_and_changed_resources = db_project.resources.filter(
        path__in=list(added_paths or []) + list(changed_paths or [])
    ).distinct()

    # We should also sync files for which source file change - but only for read-only locales.
    # See bug 1372151 for more details.
    if added_and_changed_resources:
        changed_locales_pks = [l.pk for l in locales]
        readonly_locales_pks = [l.pk for l in readonly_locales]
        locales = db_project.locales.filter(
            pk__in=changed_locales_pks + readonly_locales_pks
        )

    have_repos_changed = has_source_repo_changed
    repo_locales = None

    if not no_pull:
        repo_locales = {db_project.source_repository.pk: Locale.objects.none()}

        # Pull repos of locales in case of multi_locale_project
        if not db_project.has_single_repo:
            log.info(
                "Pulling locale repos for project {0} started.".format(db_project.slug)
            )
            have_locale_repos_changed, pulled_repo_locales = pull_locale_repo_changes(
                db_project, locales
            )
            log.info(
                "Pulling locale repos for project {0} complete.".format(db_project.slug)
            )

            have_repos_changed |= have_locale_repos_changed
            repo_locales.update(pulled_repo_locales)

    # If none of the repos has changed since the last sync and there are
    # no Pontoon-side changes for this project, quit early.
    if (
        not force
        and not db_project.needs_sync
        and not have_repos_changed
        and not (added_paths or removed_paths or changed_paths)
    ):
        log.info("Skipping project {0}, no changes detected.".format(db_project.slug))
        repo_sync_log.end()
        return

    vcs_project = VCSProject(
        db_project,
        now,
        locales=locales,
        repo_locales=repo_locales,
        added_paths=added_paths,
        changed_paths=changed_paths,
        force=force,
    )

    synced_locales = set()
    failed_locales = set()

    # Store newly added locales and locales with newly added resources
    new_locales = []

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
                if (
                    vcs_project.synced_locales
                    and locale not in vcs_project.synced_locales
                ):
                    continue

                changeset = ChangeSet(db_project, vcs_project, now, locale)
                update_translations(db_project, vcs_project, locale, changeset)
                changeset.execute()

                created = update_translated_resources(db_project, vcs_project, locale)
                if created:
                    new_locales.append(locale.pk)
                update_locale_project_locale_stats(locale, db_project)

                # Clear out the "has_changed" markers now that we've finished
                # syncing.
                (
                    ChangedEntityLocale.objects.filter(
                        entity__resource__project=db_project,
                        locale=locale,
                        when__lte=now,
                    ).delete()
                )

                # Perform the commit last so that, if it succeeds, there is
                # nothing after it to fail.
                if (
                    not no_commit
                    and locale in changeset.locales_to_commit
                    and locale not in readonly_locales
                ):
                    commit_changes(db_project, vcs_project, changeset, locale)

                log.info(
                    "Synced locale {locale} for project {project}.".format(
                        locale=locale.code, project=db_project.slug,
                    )
                )

                synced_locales.add(locale.code)

        except CommitToRepositoryException as err:
            # Transaction aborted, log and move on to the next locale.
            log.warning(
                "Failed to sync locale {locale} for project {project} due to "
                "commit error: {error}".format(
                    locale=locale.code, project=db_project.slug, error=err,
                )
            )

            failed_locales.add(locale.code)

    # If sources have changed, update stats for all locales.
    if added_paths or removed_paths or changed_paths:
        for locale in db_project.locales.all():
            # Already synced.
            if locale.code in synced_locales:
                continue

            # We have files: update all translated resources.
            if locale in locales:
                created = update_translated_resources(db_project, vcs_project, locale)
                if created:
                    new_locales.append[locale.pk]

            # We don't have files: we can still update asymmetric translated resources.
            else:
                update_translated_resources_no_files(
                    db_project, locale, added_and_changed_resources,
                )

            update_locale_project_locale_stats(locale, db_project)
            synced_locales.add(locale.code)

            log.info(
                "Synced source changes for locale {locale} for project {project}.".format(
                    locale=locale.code, project=db_project.slug,
                )
            )

        db_project.aggregate_stats()

    if synced_locales:
        log.info(
            "Synced translations for project {0} in locales {1}.".format(
                db_project.slug, ",".join(synced_locales)
            )
        )
    elif failed_locales:
        log.info(
            "Failed to sync translations for project {0} due to commit error.".format(
                db_project.slug
            )
        )
    else:
        log.info(
            "Skipping syncing translations for project {0}, none of the locales "
            "has anything to sync.".format(db_project.slug)
        )

    if repo_locales:
        repos = db_project.repositories.filter(pk__in=repo_locales.keys())
        for r in repos:
            r.set_last_synced_revisions(
                locales=repo_locales[r.pk].exclude(code__in=failed_locales)
            )
    repo_sync_log.end()

    if db_project.pretranslation_enabled:
        # Pretranslate all entities for newly added locales
        # and locales with newly added resources
        if len(new_locales):
            pretranslate(db_project.pk, locales=new_locales)

        locales = db_project.locales.exclude(pk__in=new_locales).values_list(
            "pk", flat=True
        )

        # Pretranslate newly added entities for all locales
        if new_entities and locales:
            new_entities = list(set(new_entities))
            pretranslate(db_project.pk, locales=locales, entities=new_entities)
