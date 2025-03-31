import logging

from django.core.management.base import BaseCommand
from django.db.models import Count

from pontoon.base.models import Project
from pontoon.sync.core.stats import update_stats


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
        Re-calculate statistics for all translated resources and corresponding
        objects.

        Note: while unlikely, it's possible that running this command may
        result in IntegrityErrors. That happens if at the same time when
        calculate_stats() is being executed for a TranslatedResource instance,
        translation is added, accepted or rejected for that very instance.

        To be completely sure errors don't occur, command needs to run in a
        maintenance mode.

        See bug 1470337 for more details.
        """

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Run on all projects, including disabled",
        )

    def handle(self, *args, **options):
        if options["all"]:
            projects = Project.objects.all()
            action_txt = "all projects"
        else:
            projects = Project.objects.filter(disabled=False)
            action_txt = "enabled projects"
        projects = projects.annotate(resource_count=Count("resources")).order_by(
            "disabled", "resource_count"
        )
        log.info(f"Calculating stats for {action_txt} ({len(projects)})...")

        for project in projects:
            update_stats(project)

        log.info("Calculating stats complete.")
