import logging

from django.core.management.base import BaseCommand
from django.db.models import Count

from pontoon.base.models import (
    Project,
    TranslatedResource,
)


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

    def handle(self, *args, **options):
        # Start with enabled projects in ascending order of resource count
        projects = Project.objects.annotate(resource_count=Count("resources")).order_by(
            "disabled", "resource_count"
        )

        for index, project in enumerate(projects):
            log.info(
                u'Calculating stats for project "{project}" ({index}/{total})'.format(
                    index=index + 1, total=len(projects), project=project.name,
                )
            )

            translated_resources = TranslatedResource.objects.filter(
                resource__project=project
            )

            for translated_resource in translated_resources:
                translated_resource.calculate_stats()

        log.info("Calculating stats complete for all projects.")
