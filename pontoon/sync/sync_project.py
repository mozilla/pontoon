import logging

from django.utils import timezone
from notifications.signals import notify

from pontoon.base.models import ChangedEntityLocale, Locale, Project, User
from pontoon.sync.checkouts import get_checkouts
from pontoon.sync.models import ProjectSyncLog, RepositorySyncLog, SyncLog
from pontoon.sync.paths import get_paths
from pontoon.sync.sync_entities_from_repo import sync_entities_from_repo
from pontoon.sync.sync_translations_from_repo import sync_translations_from_repo
from pontoon.sync.sync_translations_to_repo import sync_translations_to_repo

log = logging.getLogger(__name__)


def sync_project(
    project_pk: int,
    sync_log_pk: int,
    pull: bool = True,
    commit: bool = True,
    force: bool = False,
):
    try:
        project = Project.objects.get(pk=project_pk)
        sync_log = SyncLog.objects.get(pk=sync_log_pk)
    except Project.DoesNotExist:
        log.error(f"Could not sync project with pk={project_pk}, not found.")
        raise
    except SyncLog.DoesNotExist:
        log.error(
            f"Could not sync project {project.slug}, log with pk={sync_log_pk} not found."
        )
        raise

    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    log_prefix = f"[{project.slug}]"
    log.info(f"{log_prefix} Sync start")
    project_sync_log = ProjectSyncLog.objects.create(
        sync_log=sync_log, project=project, start_time=now
    )

    try:
        checkouts = get_checkouts(project, pull)
        paths = get_paths(project, checkouts)
    except Exception as e:
        log.error(f"{log_prefix} {e}")
        project_sync_log.skip()
        raise e

    locale_map: dict[str, Locale] = {
        lc.code: lc for lc in project.locales.order_by("code")
    }
    paths.locales = list(locale_map.keys())
    added_entities_count, changed_paths, removed_paths = sync_entities_from_repo(
        project, locale_map, checkouts.source, paths, now
    )

    repo_sync_log = RepositorySyncLog.objects.create(
        project_sync_log=project_sync_log,
        repository=checkouts.target.repo,
        start_time=timezone.now(),
    )

    db_changes = ChangedEntityLocale.objects.filter(
        entity__resource__project=project, when__lte=now
    ).select_related("entity__resource", "locale")
    sync_translations_from_repo(project, locale_map, checkouts, paths, db_changes, now)
    if added_entities_count > 0:
        notify_users(project, added_entities_count)
    sync_translations_to_repo(
        project,
        commit,
        locale_map,
        checkouts,
        paths,
        db_changes,
        changed_paths,
        removed_paths,
        now,
    )
    db_changes.delete()
    # have_repos_changed = any(co.commit is None or co.commit != co.prev_commit for co in checkouts)
    # pulled_revisions = {co.locale_code or "single_locale": co.commit for co in checkouts}
    log.info(f"{log_prefix} Sync done")
    repo_sync_log.end()


def notify_users(project: Project, count: int) -> None:
    users = User.objects.filter(
        translation__entity__resource__project=project,
        profile__new_string_notifications=True,
    ).distinct()
    new_strings = f"{count} new {'string' if count == 1 else 'strings'}"
    log.info(f"[{project.slug}] Notifying {len(users)} users about {new_strings}")
    for user in users:
        notify.send(project, recipient=user, verb=f"updated with {new_strings}")
