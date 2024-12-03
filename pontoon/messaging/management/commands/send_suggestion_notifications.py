import calendar

from collections import defaultdict
from datetime import timedelta
from functools import cached_property

from notifications.signals import notify

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Prefetch, Q
from django.template.loader import render_to_string
from django.utils import timezone

from pontoon.base.models import Comment, Locale, ProjectLocale, Translation


class Command(BaseCommand):
    help = "Notify contributors about newly added unreviewed suggestions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="Force run command, regardless of what day of the week it is",
        )

    @cached_property
    def locale_reviewers(self):
        locales = Locale.objects.prefetch_related(
            Prefetch("managers_group__user_set", to_attr="fetched_managers"),
            Prefetch("translators_group__user_set", to_attr="fetched_translators"),
        )

        locale_reviewers = {}

        for locale in locales:
            managers = locale.managers_group.fetched_managers
            translators = locale.translators_group.fetched_translators
            locale_reviewers[locale] = managers + translators

        return locale_reviewers

    def extract_notifications_data(self, data, suggestion):
        locale = suggestion.locale
        entity = suggestion.entity
        project = entity.resource.project
        project_locale = ProjectLocale.objects.get(project=project, locale=locale)

        translations = Translation.objects.filter(entity=entity, locale=locale)
        recipients = set()

        # Users with permission to review suggestions
        recipients = recipients.union(self.locale_reviewers[locale])

        # Authors of previous translations of the same string
        recipients = recipients.union(User.objects.filter(translation__in=translations))

        # Authors of comments of previous translations
        translations_comments = Comment.objects.filter(translation__in=translations)
        recipients = recipients.union(
            User.objects.filter(comment__in=translations_comments)
        )

        # Authors of team comments of the same string
        team_comments = Comment.objects.filter(entity=entity, locale=locale)
        recipients = recipients.union(User.objects.filter(comment__in=team_comments))

        for recipient in recipients:
            data[recipient].add(project_locale)

    def get_suggestions(self):
        start = timezone.now() - timedelta(days=7)

        return Translation.objects.filter(
            approved=False, pretranslated=False, rejected=False, fuzzy=False
        ).filter(
            Q(date__gt=start)
            | Q(unapproved_date__gt=start)
            | Q(unrejected_date__gt=start)
        )

    def handle(self, *args, **options):
        """
        This command sends notifications about newly created unreviewed suggestions that
        were submitted, unapproved or unrejected in the last 7 days. Recipients of
        notifications are users with permission to review them, as well as authors of
        previous translations or comments of the same string.

        The command is designed to run on a weekly basis.
        """
        self.stdout.write("Sending suggestion notifications.")

        today = calendar.day_name[timezone.datetime.today().weekday()]
        day = calendar.day_name[settings.SUGGESTION_NOTIFICATIONS_DAY]

        if today != day and not options["force"]:
            raise CommandError(f"Skipping. Command runs every {day}. Today is {today}.")

        suggestions = self.get_suggestions()

        data = defaultdict(set)

        for suggestion in suggestions:
            self.extract_notifications_data(data, suggestion)

        pks = [user.pk for user in data.keys()]
        recipients = User.objects.filter(
            pk__in=pks, profile__unreviewed_suggestion_notifications=True
        )

        for recipient in recipients:
            project_locales = data[recipient]

            description = render_to_string(
                "projects/suggestion_notification.jinja",
                {"project_locales": project_locales},
            )

            notify.send(
                recipient,
                recipient=recipient,
                verb="",
                description=description,
                category="unreviewed_suggestion",
            )

        self.stdout.write(f"Suggestion notifications sent to {len(recipients)} users.")
