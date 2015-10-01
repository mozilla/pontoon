import logging

from celery import shared_task

from pontoon.base.models import Project
from pontoon.sync.core import sync_project as perform_sync


log = logging.getLogger(__name__)


@shared_task
def sync_project(project_pk, no_pull=False, no_commit=False):
    """Fetch the project with the given PK and perform sync on it."""
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        log.error('Could not sync project with pk={0}, not found.'.format(project_pk))
        return

    log.info('Syncing project {0}.'.format(project.slug))
    perform_sync(project, no_pull=no_pull, no_commit=no_commit)
