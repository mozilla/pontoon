
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pontoon.administration.views import _update_from_repository
from pontoon.base.models import Project

class Command(BaseCommand):
    help = 'Update all projects from their repositories and store changes to the database'

    def handle(self, *args, **options):
        for project in Project.objects.all():
            try:
                repository_type = project.repository_type
                repository_url = project.repository
                repository_path_master = os.path.join(settings.MEDIA_ROOT,
                    repository_type, project.name)

                _update_from_repository(
                    project, repository_type, repository_url,
                    repository_path_master)
                self.stdout.write('Successfully updated project "%s"' % project)
            except Exception as e:
                raise CommandError('UpdateProjectsFromRepositoryError: %s' % unicode(e))
