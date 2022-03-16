from collections import defaultdict
from datetime import timedelta
from urllib.parse import urlencode

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from notifications.signals import notify
from pontoon.base.models import Translation


class Command(BaseCommand):
    help = "Notify translators about their newly reviewed suggestions"

    def get_description(self, author, locale, project, approved, rejected):
        url = reverse(
            "pontoon.translate",
            kwargs={
                "locale": locale.code,
                "project": project.slug,
                "resource": "all-resources",
            },
        )
        if len(approved) == 1 and len(rejected) == 0:
            url += "?" + urlencode({"string": approved[0]})
        elif len(approved) == 0 and len(rejected) == 1:
            url += "?" + urlencode({"string": rejected[0]})
        else:
            url += "?" + urlencode({"author": author.email})

        if len(approved) == 0:
            if len(rejected) == 1:
                msg = "one of your suggestions was rejected"
            else:
                msg = f"{len(rejected)} of your suggestions were rejected"
        else:
            if len(approved) == 1:
                msg = "one of your suggestions was approved"
            else:
                msg = f"{len(approved)} of your suggestions were approved"
            if len(rejected) == 1:
                msg += ", and one was rejected"
            elif len(rejected) > 1:
                msg += f", and {len(rejected)} were rejected"

        return f'In {project.name} ({locale.name}), <a href="{url}">{msg}</a>.'

    def handle(self, *args, **options):
        """
        This command sends notifications about newly reviewed
        suggestions to the authors of those suggestions.

        The command is designed to run on a daily basis.
        """
        self.stdout.write("Sending review notifications.")

        # (author, locale, project) -> (approved, rejected)
        data = defaultdict(lambda: (list(), list()))
        start = timezone.now() - timedelta(days=1)
        for suggestion in Translation.objects.filter(
            Q(approved_date__gt=start) | Q(rejected_date__gt=start)
        ):
            author = suggestion.user
            if not author.profile.review_notifications:
                continue
            locale = suggestion.locale
            project = suggestion.entity.resource.project
            key = (author, locale, project)

            if suggestion.approved and suggestion.active:
                data[key][0].append(suggestion.entity.pk)
            elif suggestion.rejected:
                data[key][1].append(suggestion.entity.pk)

        for ((author, locale, project), (approved, rejected)) in data.items():
            # Filter out rejections where the author's own suggestion replaced the previous
            rejected = [x for x in rejected if x not in approved]

            desc = self.get_description(author, locale, project, approved, rejected)
            notify.send(
                sender=author,
                recipient=author,
                verb="has reviewed suggestions",
                description=desc,
            )

        self.stdout.write(f"Sent {len(data)} review notifications.")
