from django.core.management.base import BaseCommand

from pontoon.base.models import TranslatedResource


class Command(BaseCommand):
    help = ('Re-calculate statistics for all translated resources and '
            'corresponding objects.')

    def handle(self, *args, **options):
        for tr in TranslatedResource.objects.order_by(
            'resource__project__disabled',
            '-resource__project__priority'
        ):
            tr.calculate_stats()
