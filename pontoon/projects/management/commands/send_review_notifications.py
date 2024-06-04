from collections import defaultdict
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from notifications.signals import notify
from pontoon.base.models import Translation


class Command(BaseCommand):
    help = "Notify translators about their newly reviewed suggestions"

    def get_description(self, notifyData):
        desc = "Your suggestions have been reviewed:\n<ul>"

        for (locale, project), (approved, rejected) in notifyData.items():
            url = reverse(
                "pontoon.translate",
                kwargs={
                    "locale": locale.code,
                    "project": project.slug,
                    "resource": "all-resources",
                },
            )
            list = map(str, approved + rejected)
            url += "?list=" + ",".join(list)

            # Filter out rejections where the author's own suggestion replaced the previous
            rejected = [x for x in rejected if x not in approved]

            if len(approved) == 0:
                msg = f"{len(rejected)} Rejected"
            else:
                msg = f"{len(approved)} Approved"
                if len(rejected) > 0:
                    msg += f", {len(rejected)} Rejected"

            desc += (
                f'\n<li><a href="{url}">{project.name} ({locale.code})</a>: {msg}</li>'
            )

        return desc + "\n</ul>"

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
        ):
            author = suggestion.user
            locale = suggestion.locale
            project = suggestion.entity.resource.project

            if suggestion.approved and suggestion.approved_user != author:
                data[author][(locale, project)][0].append(suggestion.entity.pk)
            elif suggestion.rejected and suggestion.rejected_user != author:
                data[author][(locale, project)][1].append(suggestion.entity.pk)

        for author, notifyData in data.items():
            desc = self.get_description(notifyData)
            notify.send(
                sender=author,
                recipient=author,
                verb="has reviewed suggestions",
                description=desc,
            )

        self.stdout.write(f"Sent {len(data)} review notifications.")
