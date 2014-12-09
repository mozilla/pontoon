
import datetime

from django.core.management.base import BaseCommand, CommandError

from pontoon.administration.files import (
    update_from_repository,
    extract_to_database,
)

from pontoon.base.models import Project


class Command(BaseCommand):
    args = '<project_id project_id ...>'
    help = 'Update projects from repositories and store changes to database'

    def handle(self, *args, **options):
        projects = Project.objects.all()
        if args:
            projects = projects.filter(pk__in=args)

        for project in projects:
            try:
                update_from_repository(project)
                extract_to_database(project)
                now = datetime.datetime.now()
                self.stdout.write(
                    '[%s]: Updated project "%s"\n' %
                    (now, project))
            except Exception as e:
                now = datetime.datetime.now()
                raise CommandError(
                    '[%s]: Update Projects Error: %s\n' % (now, unicode(e)))
