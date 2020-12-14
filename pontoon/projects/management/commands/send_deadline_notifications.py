import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from notifications.signals import notify

from pontoon.base.models import Project


class Command(BaseCommand):
    help = "Notify contributors about the approaching project deadline"

    def handle(self, *args, **options):
        """
        This command sends deadline reminders to contributors of projects that
        are due in 7 days. If 2 days before the deadline project still isn't
        complete for the contributor's locale, notifications are sent again.

        The command is designed to run daily.
        """
        for project in Project.objects.available():
            if project.deadline:
                days_left = (project.deadline - datetime.date.today()).days
                if days_left not in (2, 7):
                    continue
            else:
                continue

            self.stdout.write(
                "Sending deadline notifications for project {}.".format(project)
            )

            verb = "due in {} days".format(days_left)
            locales = []

            for project_locale in project.project_locale.all():
                if project_locale.approved_strings < project_locale.total_strings:
                    locales.append(project_locale.locale)

            contributors = (
                User.projects.filter_by_visibility(project)
                .filter(
                    translation__entity__resource__project=project,
                    translation__locale__in=locales,
                )
                .distinct(),
            )

            for contributor in contributors:
                notify.send(project, recipient=contributor, verb=verb)

            self.stdout.write(
                "Deadline notifications for project {} sent.".format(project)
            )
