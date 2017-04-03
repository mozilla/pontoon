import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from notifications.signals import notify

from pontoon.base.models import Project


class Command(BaseCommand):
    help = 'Notify contributors about the approaching project deadline'

    def handle(self, *args, **options):
        """
        This command sends deadline reminders to contributors of projects that
        are due in 7 days. If 2 days before the deadline project still isn't
        complete for the contributor's locale, notifications are sent again.

        Command is designed to run on a daily basis.
        """
        for project in Project.objects.available():
            if project.deadline:
                days_left = (project.deadline - datetime.date.today()).days
                if days_left not in (2, 7):
                    continue
            else:
                continue

            for project_locale in project.project_locale.all():
                if project_locale.approved_strings < project_locale.total_strings:
                    verb = 'due in {} days'.format(days_left)

                    translators = User.objects.filter(
                        translation__entity__resource__project=project,
                        translation__locale=project_locale.locale
                    ).distinct()

                    for user in translators:
                        notify.send(
                            project,
                            recipient=user,
                            verb=verb
                        )
