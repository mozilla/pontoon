from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pontoon.base.models import Project
from pontoon.sync.models import SyncLog
from pontoon.sync.tasks import sync_project


class Command(BaseCommand):
    help = "Synchronize database and remote repositories."

    def add_arguments(self, parser):
        parser.add_argument(
            "--projects",
            action="store",
            dest="projects",
            default="",
            help="Sync only projects within this comma-separated list of slugs",
        )

        parser.add_argument(
            "--no-commit",
            action="store_true",
            dest="no_commit",
            default=False,
            help="Do not commit changes to VCS",
        )

        parser.add_argument(
            "--no-pull",
            action="store_true",
            dest="no_pull",
            default=False,
            help="Do not pull new commits from VCS",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="Always sync even if there are no changes",
        )

    def handle(self, *args, **options):
        """
        Collect the projects we want to sync and trigger worker jobs to
        sync each one.
        """
        sync_log = SyncLog.objects.create(start_time=timezone.now())

        if options["force"]:
            projects = Project.objects.force_syncable()
        else:
            projects = Project.objects.syncable()

        slugs = (
            options["projects"].split(",")
            if "projects" in options and options["projects"]
            else None
        )
        if slugs:
            projects = projects.filter(slug__in=slugs)

        if len(projects) < 1:
            raise CommandError("No matching projects to sync found.")

        if slugs and len(projects) != len(slugs):
            invalid_slugs = sorted(
                set(slugs).difference(set(projects.values_list("slug", flat=True)))
            )
            self.stderr.write(
                "Couldn't find projects to sync with following slugs: {}".format(
                    ", ".join(invalid_slugs)
                )
            )

        for project in projects:
            if not project.can_commit:
                self.stdout.write(
                    u"Skipping project {0}, cannot commit to repository.".format(
                        project.name
                    )
                )
            else:
                self.stdout.write(
                    u"Scheduling sync for project {0}.".format(project.name)
                )
                sync_project.delay(
                    project.pk,
                    sync_log.pk,
                    no_pull=options["no_pull"],
                    no_commit=options["no_commit"],
                    force=options["force"],
                )
