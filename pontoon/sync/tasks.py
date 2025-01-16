import logging

from celery import shared_task

from django.conf import settings
from django.core.cache import cache

from pontoon.base.models import Project
from pontoon.base.tasks import PontoonTask
from pontoon.sync.core import sync_project
from pontoon.sync.models import Sync


log = logging.getLogger(__name__)


@shared_task(base=PontoonTask, name="sync_project")
def sync_project_task(
    project_pk: int,
    pull: bool = True,
    commit: bool = True,
    force: bool = False,
):
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        log.error(f"[id={project_pk}] Sync aborted: Project not found.")
        raise

    sync = Sync.objects.create(project=project)
    lock_name = f"sync_{project_pk}"
    if not cache.add(lock_name, True, timeout=settings.SYNC_TASK_TIMEOUT):
        sync.done(Sync.Status.PREV_BUSY)
        raise RuntimeError(
            f"[{project.slug}] Sync aborted: Previous sync still running."
        )
    try:
        with_changes = sync_project(project, pull=pull, commit=commit, force=force)
        if not with_changes:
            status = Sync.Status.NO_CHANGES
        elif not commit:
            status = Sync.Status.NO_COMMIT
        else:
            status = Sync.Status.DONE
        sync.done(status)
    except Exception as err:
        sync.fail(str(err))
    finally:
        # release the lock
        cache.delete(lock_name)
