from collections import defaultdict
from datetime import timedelta

from notifications.signals import notify

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from pontoon.base.models import Translation


class Command(BaseCommand):
    help = "Notify translators about their newly reviewed suggestions"

    def handle(self, *args, **options):
        """
        This command sends notifications about newly reviewed
        suggestions to the authors of those suggestions.

        The command is designed to run on a daily basis.
        """
        self.stdout.write("Sending review notifications...")

        # (author) -> (locale, project) -> (approved, rejected)
        data = defaultdict(lambda: defaultdict(lambda: (list(), list())))
        start = timezone.now() - timedelta(days=1)

        for suggestion in Translation.objects.filter(
            (Q(approved_date__gt=start) | Q(rejected_date__gt=start))
            & Q(user__profile__review_notifications=True)
            & Q(entity__resource__project__disabled=False)
        ):
            author = suggestion.user
            locale = suggestion.locale
            project = suggestion.entity.resource.project

            if suggestion.approved and suggestion.approved_user != author:
                data[author][(locale, project)][0].append(suggestion.entity.pk)
            elif suggestion.rejected and suggestion.rejected_user != author:
                data[author][(locale, project)][1].append(suggestion.entity.pk)

        for author, notification_data in data.items():
            notifications = []

            for (locale, project), (approved, rejected) in notification_data.items():
                # Filter out rejections where the author's own suggestion replaced the previous
                rejected = [id for id in rejected if id not in approved]

                if len(approved) == 0:
                    msg = f"{len(rejected)} Rejected"
                else:
                    msg = f"{len(approved)} Approved"
                    if len(rejected) > 0:
                        msg += f", {len(rejected)} Rejected"

                notifications.append(
                    {
                        "locale": locale,
                        "project": project,
                        "ids": ",".join(map(str, approved + rejected)),
                        "msg": msg,
                    }
                )

            description = render_to_string(
                "messaging/notifications/suggestions_reviewed.html",
                {
                    "notifications": notifications,
                },
            )

            notify.send(
                sender=author,
                recipient=author,
                verb="has reviewed suggestions",
                description=description,
                category="review",
            )

        self.stdout.write(f"Sent {len(data)} review notifications.")
