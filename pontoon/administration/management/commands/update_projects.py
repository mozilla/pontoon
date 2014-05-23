
import datetime

from django.core.management.base import BaseCommand, CommandError

from pontoon.administration.utils.files import (
    update_from_repository,
    extract_to_database,
)

from pontoon.base.models import Project


class Command(BaseCommand):
    help = 'Update all projects from their repositories and store changes \
            to the database'

    def handle(self, *args, **options):
        for project in Project.objects.all():
            try:
                update_from_repository(project)
                extract_to_database(project)
                now = datetime.datetime.now()
                self.stdout.write(
                    '[%s]: Successfully updated project "%s"\n' %
                    (now, project))
            except Exception as e:
                now = datetime.datetime.now()
                raise CommandError(
                    '[%s]: UpdateProjectsFromRepositoryError: %s\n' %
                    (now, unicode(e)))
