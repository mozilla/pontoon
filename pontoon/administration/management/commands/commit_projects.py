
import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from pontoon.administration.files import dump_from_database
from pontoon.administration.vcs import commit_to_vcs
from pontoon.base.models import Project


class Command(BaseCommand):
    args = '<project_id project_id ...>'
    help = 'Store projects to filesystem and commit changes to repositories'

    def handle(self, *args, **options):
        def output(message, success):
            now = datetime.datetime.now()
            if success:
                self.stdout.write('[%s]: %s\n' % (now, message))
            else:
                raise CommandError(message)

        projects = Project.objects.all()
        if args:
            projects = projects.filter(pk__in=args)

        for project in projects:
            if project.repository_type not in ('git', 'hg', 'svn'):
                continue
            for locale in project.locales.all():

                path = dump_from_database(project, locale)
                if not path:
                    output('Repository path not found')

                repo_type = project.repository_type
                message = 'Pontoon: Update %s (%s) localization of %s.' \
                    % (locale.name, locale.code, project.name)
                user = User.objects.filter(is_superuser=True)[0]

                try:
                    r = commit_to_vcs(repo_type, path, message, user, {})
                except Exception as e:
                    output('Commit Projects Error: %s' % unicode(e))
                if r is not None:
                    output('Commit Projects Error: %s' % r.message)

                output('Commited project %s for %s (%s)' %
                       (project, locale.name, locale.code), True)
