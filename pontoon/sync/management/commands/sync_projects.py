from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pontoon.base.models import Locale, Project
from pontoon.sync.models import SyncLog
from pontoon.sync.tasks import sync_project


class Command(BaseCommand):
    help = 'Synchronize database and remote repositories.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--projects',
            action='store',
            dest='projects',
            default='',
            help='Sync only projects within this comma-separated list of slugs'
        )

        parser.add_argument(
            '--locale',
            action='store',
            dest='locale',
            default=None,
            help='Sync only locale with this locale code'
        )

        parser.add_argument(
            '--no-commit',
            action='store_true',
            dest='no_commit',
            default=False,
            help='Do not commit changes to VCS'
        )

        parser.add_argument(
            '--no-pull',
            action='store_true',
            dest='no_pull',
            default=False,
            help='Do not pull new commits from VCS'
        )

        parser.add_argument(
            '-f', '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Always sync even if there are no changes'
        )

        parser.add_argument(
            '-s', '--synchronous',
            action='store_true',
            dest='force',
            default=False,
            help='Run the task synchronously'
        )

    def handle(self, *args, **options):
        """
        Collect the projects we want to sync and trigger worker jobs to
        sync each one.
        """
        sync_log = SyncLog.objects.create(start_time=timezone.now())

        projects = Project.objects.syncable()
        slugs = (
            options['projects'].split(',') if 'projects' in options and options['projects']
            else None
        )
        if slugs:
            projects = projects.filter(slug__in=slugs)

        if len(projects) < 1:
            raise CommandError('No matching projects found.')

        if slugs and len(projects) != len(slugs):
            invalid_slugs = sorted(
                set(slugs).difference(set(projects.values_list('slug', flat=True)))
            )
            self.stderr.write(
                "Couldn't find projects with following slugs: {}".format(
                    ', '.join(invalid_slugs)
                )
            )

        locale = None
        if options['locale']:
            try:
                locale = Locale.objects.get(code=options['locale'])
            except Locale.DoesNotExist:
                raise CommandError('No matching locale found.')

        for project in projects:
            if not project.can_commit:
                self.stdout.write(u'Skipping project {0}, cannot commit to repository.'
                                  .format(project.name))
            else:
                self.stdout.write(u'Scheduling sync for project {0}.'.format(project.name))
                if options['synchronous']:
                    sync_project.apply(
                        args=(project.pk, sync_log.pk),
                        kwargs=dict(
                            locale=locale,
                            no_pull=options['no_pull'],
                            no_commit=options['no_commit'],
                            force=options['force'],
                        )
                    )
                else:
                    sync_project.delay(
                        project.pk,
                        sync_log.pk,
                        locale=locale,
                        no_pull=options['no_pull'],
                        no_commit=options['no_commit'],
                        force=options['force'],
                    )
