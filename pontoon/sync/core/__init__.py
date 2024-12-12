import logging

from notifications.signals import notify

from django.utils import timezone

from pontoon.base.models import ChangedEntityLocale, Locale, Project, User
from pontoon.pretranslation.tasks import pretranslate
from pontoon.sync.core.checkout import checkout_repos
from pontoon.sync.core.entities import sync_entities_from_repo
from pontoon.sync.core.paths import find_paths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import sync_translations_from_repo
from pontoon.sync.core.translations_to_repo import sync_translations_to_repo
from pontoon.sync.models import ProjectSyncLog, RepositorySyncLog, SyncLog


log = logging.getLogger(__name__)


def sync_project(
    project: Project,
    sync_log: SyncLog,
    *,
    pull: bool = True,
    commit: bool = True,
    force: bool = False,
):
    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    log_prefix = f"[{project.slug}]"
    log.info(f"{log_prefix} Sync start")
    project_sync_log = ProjectSyncLog.objects.create(
        sync_log=sync_log, project=project, start_time=now
    )

    try:
        checkouts = checkout_repos(project, force=force, pull=pull)
        paths = find_paths(project, checkouts)
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
    del_trans_count, updated_trans_count = sync_translations_from_repo(
        project, locale_map, checkouts, paths, db_changes, now
    )
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
    checkouts.source.repo.last_synced_revision = checkouts.source.commit
    if checkouts.target != checkouts.source:
        checkouts.target.repo.last_synced_revision = checkouts.target.commit
    if (
        added_entities_count
        or changed_paths
        or removed_paths
        or del_trans_count
        or updated_trans_count
    ):
        update_stats(project)
    repo_sync_log.end()
    log.info(f"{log_prefix} Sync done")

    if project.pretranslation_enabled and changed_paths:
        # Pretranslate changed and added resources for all locales
        pretranslate(project, changed_paths)


def notify_users(project: Project, count: int) -> None:
    users = User.objects.filter(
        translation__entity__resource__project=project,
        profile__new_string_notifications=True,
    ).distinct()
    new_strings = f"{count} new {'string' if count == 1 else 'strings'}"
    log.info(f"[{project.slug}] Notifying {len(users)} users about {new_strings}")
    for user in users:
        notify.send(
            project,
            recipient=user,
            verb=f"updated with {new_strings}",
            category="new_string",
        )
