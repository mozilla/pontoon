
import commonware
import os

from celery.task import task
from django.conf import settings
from pontoon.base.models import Project
from pontoon.administration.views import _update_from_repository


log = commonware.log.getLogger('pontoon')


@task()
def update_projects_from_repository():
    for project in Project.objects.all():
        try:
            repository_type = project.repository_type
            repository_url = project.repository
            repository_path_master = os.path.join(settings.MEDIA_ROOT,
                repository_type, project.name)

            _update_from_repository(
                project, repository_type, repository_url,
                repository_path_master)
        except Exception as e:
            log.debug('UpdateFromRepositoryTaskError: %s' % unicode(e))
