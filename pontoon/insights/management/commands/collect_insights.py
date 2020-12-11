from collections import defaultdict

from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Entity, Locale, Translation
from pontoon.insights.models import LocaleInsightsSnapshot


class Command(BaseCommand):
    help = "Collect data needed for the Insights tab"

    def handle(self, *args, **options):
        """
        The Insights tab presents data that cannot be retrieved from the exisrting data
        models efficiently upon each request. This command gathers all the required data
        and stores it in a dedicated denormalized data model.

        The command is designed to run in the beginning of the day, every day. That's
        because the translation and review activity data is collected for the period of
        a (previous) day, whereas completion data (stats) is collected as the current
        snapshot. Hence, it's important that the time of taking the snapshot is as close
        to the activity period as possible.
        """
        snapshots = []

        # Set time boundaries of the previous day
        start_of_today = (
            timezone.now()
            .replace(hour=0)
            .replace(minute=0)
            .replace(second=0)
            .replace(microsecond=0)
        )
        start_of_yesterday = start_of_today - timedelta(days=1)

        # Get all and active managers, and all translators
        privileged_users = (
            Locale.objects.available()
            .prefetch_related(
                "managers_group__user_set", "translators_group__user_set",
            )
            .values(
                "pk",
                "managers_group__user__last_login",
                "managers_group__user",
                "translators_group__user",
            )
        )

        # Get all contributors
        contributors = (
            Translation.objects.filter(user__isnull=False)
            .values("locale", "user",)
            .distinct()
        )
        # Excluded (system) users: excluding directly in the above QuerySet is slow
        excluded_users = User.objects.filter(
            email__regex=r"^pontoon-(\w+)@example.com$",
        ).values("pk")
        contributors = [c for c in contributors if c["user"] not in excluded_users]

        # Get user translation and review actions
        user_actions = (
            ActionLog.objects.filter(
                created_at__gte=start_of_today - timedelta(days=365),
                created_at__lt=start_of_today,
            )
            .values("action_type", "performed_by", "translation__locale",)
            .distinct()
        )

        # Get current unreviewed suggestions
        suggestions = Translation.objects.filter(
            approved=False,
            fuzzy=False,
            rejected=False,
            entity__obsolete=False,
            entity__resource__project__disabled=False,
            entity__resource__project__system_project=False,
            entity__resource__project__visibility="public",
        ).values("locale", "date",)

        # Get actions of the previous day
        actions = (
            ActionLog.objects.filter(
                created_at__gte=start_of_yesterday,
                created_at__lt=start_of_today,
                translation__entity__resource__project__system_project=False,
                translation__entity__resource__project__visibility="public",
            )
            .prefetch_related("translation__errors")
            .prefetch_related("translation__warnings")
            .values(
                "action_type",
                "translation",
                "translation__locale",
                "translation__approved",
                "translation__fuzzy",
                "translation__rejected",
                "translation__errors",
                "translation__warnings",
                "translation__machinery_sources",
                "translation__user",
                "translation__approved_user",
            )
        )

        # Get entities created on the previous day
        entities = Entity.objects.filter(
            date_created__gte=start_of_yesterday,
            date_created__lt=start_of_today,
            obsolete=False,
            resource__project__disabled=False,
            resource__project__system_project=False,
            resource__project__visibility="public",
        ).values("pk", "resource__translatedresources__locale",)

        def group_by(list_of_dictionaries, key):
            group = defaultdict(list)

            for dictionary in list_of_dictionaries:
                group[dictionary[key]].append(dictionary)

            return group

        # Group actions, suggestions, entities, users by locale
        grouped_privileged_users = group_by(privileged_users, "pk")
        grouped_contributors = group_by(contributors, "locale")
        grouped_user_actions = group_by(user_actions, "translation__locale")
        grouped_suggestions = group_by(suggestions, "locale")
        grouped_actions = group_by(actions, "translation__locale")
        grouped_entities = group_by(entities, "resource__translatedresources__locale")

        # Collect insights for each locale
        for locale in Locale.objects.available():
            snapshot = self.handle_locale(
                locale,
                start_of_today,
                grouped_privileged_users[locale.id],
                grouped_contributors[locale.id],
                grouped_user_actions[locale.id],
                grouped_suggestions[locale.id],
                grouped_actions[locale.id],
                grouped_entities[locale.id],
            )

            snapshots.append(snapshot)

        LocaleInsightsSnapshot.objects.bulk_create(snapshots)

        self.stdout.write("Locale insights created.")

    def handle_locale(
        self,
        locale,
        start_of_today,
        privileged_users,
        contributors,
        user_actions,
        suggestions,
        actions,
        entities,
    ):
        """
        Collect and store insights for each locale
        """
        # Get total users for the Active users panel
        all_managers = set()
        all_reviewers = set()
        all_contributors = {c["user"] for c in contributors}

        for user in privileged_users:
            manager = user["managers_group__user"]
            translator = user["translators_group__user"]

            if manager:
                all_managers.add(manager)
                all_reviewers.add(manager)
            if translator:
                all_reviewers.add(translator)

        total_managers = len(all_managers)
        total_reviewers = len(all_reviewers)
        total_contributors = len(all_contributors)

        # Get active users for the Active users panel
        active_managers = set()
        active_reviewers = set()
        active_contributors = set()

        for user in privileged_users:
            manager = user["managers_group__user"]
            last_login = user["managers_group__user__last_login"]

            if last_login:
                if start_of_today - last_login < timedelta(days=365):
                    active_managers.add(manager)

        # Make sure active users are included among all users, otherwise we might
        # include PMs and privileged users of other locales
        for action in user_actions:
            user = action["performed_by"]
            if user in all_reviewers and action["action_type"] in (
                "translation:approved",
                "translation:unapproved",
                "translation:rejected",
                "translation:unrejected",
            ):
                active_reviewers.add(user)
            if (
                user in all_contributors
                and action["action_type"] == "translation:created"
            ):
                active_contributors.add(user)

        active_users_last_12_months = {
            "managers": len(active_managers),
            "reviewers": len(active_reviewers),
            "contributors": len(active_contributors),
        }

        # Get data for the Unreviewed suggestions lifespan chart
        unreviewed_suggestions_lifespan = timedelta()
        suggestion_count = len(suggestions)

        if suggestion_count > 0:
            total_suggestion_age = timedelta()

            for s in suggestions:
                total_suggestion_age += start_of_today - s["date"]

            unreviewed_suggestions_lifespan = total_suggestion_age / suggestion_count

        # Get data for Translation activity and Review activity charts
        human_translations = set()
        machinery_translations = set()
        new_suggestions = set()
        peer_approved = set()
        self_approved = set()
        rejected = set()

        for action in actions:
            action_type = action["action_type"]
            translation = action["translation"]
            is_approved = action["translation__approved"]
            is_fuzzy = action["translation__fuzzy"]
            is_rejected = action["translation__rejected"]
            errors = action["translation__errors"]
            warnings = action["translation__warnings"]
            machinery_sources = action["translation__machinery_sources"]
            user = action["translation__user"]
            approved_user = action["translation__approved_user"]

            if action_type == "translation:created":
                if is_approved and errors is None and warnings is None:
                    if len(machinery_sources) == 0:
                        human_translations.add(translation)
                    else:
                        machinery_translations.add(translation)

                elif not is_approved and not is_fuzzy and not is_rejected:
                    new_suggestions.add(translation)

            elif action_type == "translation:approved" and is_approved:
                if user != approved_user:
                    peer_approved.add(translation)
                else:
                    self_approved.add(translation)

            elif action_type == "translation:rejected" and is_rejected:
                rejected.add(translation)

        return LocaleInsightsSnapshot(
            locale=locale,
            created_at=start_of_today,
            # AggregatedStats
            total_strings=locale.total_strings,
            approved_strings=locale.approved_strings,
            fuzzy_strings=locale.fuzzy_strings,
            strings_with_errors=locale.strings_with_errors,
            strings_with_warnings=locale.strings_with_warnings,
            unreviewed_strings=locale.unreviewed_strings,
            # Active users
            total_managers=total_managers,
            total_reviewers=total_reviewers,
            total_contributors=total_contributors,
            active_users_last_12_months=active_users_last_12_months,
            # Unreviewed suggestions lifespan
            unreviewed_suggestions_lifespan=unreviewed_suggestions_lifespan,
            # Translation activity
            completion=round(locale.completed_percent, 2),
            human_translations=len(human_translations),
            machinery_translations=len(machinery_translations),
            new_source_strings=len(entities),
            # Review activity
            peer_approved=len(peer_approved),
            self_approved=len(self_approved),
            rejected=len(rejected),
            new_suggestions=len(new_suggestions),
        )
