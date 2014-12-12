
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
        def output(text):
            now = datetime.datetime.now()
            self.stdout.write('[%s]: %s\n' % (now, text.encode('utf8')))

        projects = Project.objects.all()
        if args:
            projects = projects.filter(pk__in=args)
        else:
            output(self.help.upper())

        for project in projects:
            try:
                update_from_repository(project)
                extract_to_database(project)
                output('Updated project %s' % project)
            except Exception as e:
                now = datetime.datetime.now()
                raise CommandError(
                    '[%s]: Update error: %s\n' % (now, unicode(e)))
