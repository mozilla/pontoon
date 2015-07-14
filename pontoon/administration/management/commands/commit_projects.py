
import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from pontoon.administration.files import dump_from_database, update_from_repository, extract_to_database
from pontoon.administration.vcs import commit_to_vcs
from pontoon.base.models import (
    Project,
    Translation,
)


class Command(BaseCommand):
    args = '<project_id project_id ...>'
    help = 'Store projects to filesystem and commit changes to repositories'

    def handle(self, *args, **options):
        def output(text):
            self.stdout.write(text + u'\n')

        output('COMMIT PROJECTS: start')

        projects = Project.objects.filter(disabled=False)
        if args:
            projects = projects.filter(pk__in=args)

        for project in projects:
            repo_type = project.repository_type

            if repo_type not in ('git', 'hg', 'svn'):
                output('Committing project %s failed: Not a VCS project' %
                       (project))
                continue

            # Update project from VCS to ensure the directory exists.
            try:
                update_from_repository(project)
                extract_to_database(project)
                output('Updated project %s' % project)
            except Exception as e:
                raise CommandError(u'Update error: %s\n' % unicode(e))

            for locale in project.locales.all():

                # Dump files from database
                path = dump_from_database(project, locale)
                if not path:
                    error = 'Repository path not found'
                    output('Committing project %s for %s (%s) failed: %s' %
                           (project, locale.name, locale.code, error))
                    continue

                message = 'Pontoon: Update %s (%s) localization of %s.' \
                    % (locale.name, locale.code, project.name)

                # Set latest translation author as commit author if available
                user = User.objects.filter(is_superuser=True)[0]
                translations = Translation.objects.exclude(user=None).filter(
                    locale=locale,
                    entity__obsolete=False,
                    entity__resource__project=project) \
                    .order_by('-date')
                if translations:
                    user = translations[0].user

                # Commit files to VCS
                try:
                    r = commit_to_vcs(repo_type, path, message, user, project.repository_url)
                except Exception as e:
                    output('Committing project %s for %s (%s) failed: %s' %
                           (project, locale.name, locale.code, unicode(e)))
                    continue
                if r is not None:
                    output('Committing project %s for %s (%s) failed: %s' %
                           (project, locale.name, locale.code, r["message"]))
                    continue

                output('Commited project %s for %s (%s)' %
                       (project, locale.name, locale.code))

        output('COMMIT PROJECTS: done')
