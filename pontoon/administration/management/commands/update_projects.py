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
            self.stdout.write(text.encode('utf8') + u'\n')

        output('UPDATE PROJECTS: start')

        projects = Project.objects.filter(disabled=False)
        if args:
            projects = projects.filter(pk__in=args)

        for project in projects:
            try:
                update_from_repository(project)
                extract_to_database(project)
                output('Updated project %s' % project)
            except Exception as e:
                raise CommandError(u'Update error: %s\n' % unicode(e))

        output('UPDATE PROJECTS: done')
