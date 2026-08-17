import logging

from datetime import timedelta

from celery import shared_task

from django.conf import settings
from django.db import transaction
from django.utils import timezone

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

    if not force:
        try:
            prev_sync = Sync.objects.filter(project=project).latest("start_time")
            if project.date_modified > prev_sync.start_time:
                log.info(
                    f"Using forced sync due to project config change on {project.date_modified}"
                )
                force = True
        except Sync.DoesNotExist:
            pass

    # Lock the project row so that two concurrent sync tasks for the same
    # project can't both observe "no active sync" and proceed. Once this
    # transaction is complete, newer tasks can rely on the Sync row.
    # The error is raised outside the atomic transaction to avoid rolling back
    # the PREV_BUSY sync row creation.
    prev_busy = False
    with transaction.atomic():
        locked_project = Project.objects.select_for_update().get(pk=project_pk)
        stale_cutoff = timezone.now() - timedelta(seconds=settings.SYNC_TASK_TIMEOUT)
        in_progress = Sync.objects.filter(
            project=locked_project, status=Sync.Status.IN_PROGRESS
        )
        prev_busy = in_progress.filter(start_time__gt=stale_cutoff).exists()
        if prev_busy:
            sync = Sync.objects.create(project=locked_project)
            sync.done(Sync.Status.PREV_BUSY)
        else:
            # Any remaining IN_PROGRESS syncs are older than the timeout, so
            # the worker that ran them likely died without reporting back.
            in_progress.update(status=Sync.Status.INCOMPLETE)
            sync = Sync.objects.create(project=locked_project)

    if prev_busy:
        raise RuntimeError(
            f"[{project.slug}] Sync aborted: Previous sync still running."
        )

    try:
        db_changed, repo_changed = sync_project(
            project, pull=pull, commit=commit, force=force
        )
        if not db_changed and not repo_changed:
            status = Sync.Status.NO_CHANGES
        elif not commit and repo_changed:
            status = Sync.Status.NO_COMMIT
        else:
            status = Sync.Status.DONE
        sync.done(status)
    except Exception as err:
        log.error(f"[{project.slug}] Sync failed: {err}")
        sync.fail(str(err))
