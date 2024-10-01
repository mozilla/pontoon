import logging

from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from pontoon.base.models import Project
from pontoon.base.tasks import PontoonTask
from pontoon.sync.core import sync_project
from pontoon.sync.models import ProjectSyncLog, SyncLog

log = logging.getLogger(__name__)


@shared_task(base=PontoonTask, name="sync_project")
def sync_project_task(
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
        log.error(f"[id={project.slug}] Sync aborted: Project not found.")
        raise
    except SyncLog.DoesNotExist:
        log.error(
            f"[{project.slug}] Sync aborted: Log with id={sync_log_pk} not found."
        )
        raise

    lock_name = f"sync {project.slug} [id={project_pk}]"
    if not cache.add(lock_name, True, timeout=settings.SYNC_TASK_TIMEOUT):
        ProjectSyncLog.objects.create(project=project, sync_log=sync_log).skip()
        raise RuntimeError(
            f"[{project.slug}] Sync aborted: Previous sync still running."
        )
    try:
        sync_project(project, sync_log, pull=pull, commit=commit, force=force)
    finally:
        # release the lock
        cache.delete(lock_name)
