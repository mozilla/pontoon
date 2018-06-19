import logging

from bulk_update.helper import bulk_update

from django.core.management.base import BaseCommand
from django.db.models import Count

from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    TranslatedResource,
)


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Re-calculate statistics for all translated resources and '
            'corresponding objects.')

    def handle(self, *args, **options):
        # Start with enabled projects in ascending order of resource count
        projects = (
            Project.objects
            .annotate(resource_count=Count('resources'))
            .order_by('disabled', 'resource_count')
        )

        for index, project in enumerate(projects):
            log.info(
                u'Calculating stats for project "{project}" ({index}/{total})'
                .format(
                    index=index+1,
                    total=len(projects),
                    project=project.name,
                )
            )

            translated_resources = (
                TranslatedResource.objects.filter(resource__project=project)
            )

            for translated_resource in translated_resources:
                translated_resource.calculate_stats(save=False)

            bulk_update(translated_resources, update_fields=[
                'total_strings',
                'approved_strings',
                'fuzzy_strings',
                'unreviewed_strings',
            ])

            project.aggregate_stats()

            project_locales = ProjectLocale.objects.filter(project=project)
            for project_locale in project_locales:
                project_locale.aggregate_stats()

        for locale in Locale.objects.all():
            locale.aggregate_stats()

        log.info('Calculating stats complete for all projects.')
