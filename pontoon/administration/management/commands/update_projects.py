
import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from pontoon.administration.views import (
    get_repository_path_master,
    update_files_from_repository,
)
from pontoon.base.models import Project


class Command(BaseCommand):
    help = 'Update all projects from their repositories and store changes \
            to the database'

    def handle(self, *args, **options):
        for project in Project.objects.all():
            try:
                repository_type = project.repository_type
                repository_url = project.repository_url
                repository_path_master = get_repository_path_master(project)

                update_files_from_repository(
                    project, repository_type, repository_url,
                    repository_path_master)
                now = datetime.datetime.now()
                self.stdout.write(
                    '[%s]: Successfully updated project "%s"\n' %
                    (now, project))
            except Exception as e:
                now = datetime.datetime.now()
                raise CommandError(
                    '[%s]: UpdateProjectsFromRepositoryError: %s\n' %
                    (now, unicode(e)))
