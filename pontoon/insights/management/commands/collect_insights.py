from django.core.management.base import BaseCommand

from pontoon.insights.tasks import collect_insights


class Command(BaseCommand):
    help = "Collect data needed for the Insights tab"

    def handle(self, *args, **options):
        """
        The Insights tab in the dashboard presents data that cannot be retrieved from
        the existing data models efficiently upon each request. This command gathers
        all the required data and stores it in a dedicated denormalized data model.

        The command is designed to run in the beginning of the day, every day. That's
        because the translation and review activity data is collected for the period of
        a (previous) day, whereas completion data (stats) is collected as the current
        snapshot. Hence, it's important that the time of taking the snapshot is as close
        to the activity period as possible.
        """
        collect_insights.delay()
