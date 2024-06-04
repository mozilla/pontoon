import logging
import statistics

from celery import shared_task
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db.models import Count, F
from django.utils import timezone
from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Entity, Locale, ProjectLocale, Translation
from pontoon.base.utils import group_dict_by
from pontoon.insights.models import (
    LocaleInsightsSnapshot,
    ProjectLocaleInsightsSnapshot,
)
from sacrebleu.metrics import CHRF


chrfpp = CHRF(word_order=2)
log = logging.getLogger(__name__)


@shared_task(bind=True)
def collect_insights(self):
    """
    Gather data needed for the Insights tab and store it in the DB.
    """
    start_of_today = (
        timezone.now()
        .replace(hour=0)
        .replace(minute=0)
        .replace(second=0)
        .replace(microsecond=0)
    )

    date = start_of_today.date()

    log.info(f"Collect insights for {date}: Begin.")

    activities = build_charts_data(start_of_today)
    entities = query_entities(start_of_today)
    log.info(f"Collect insights for {date}: Common data gathered.")

    collect_project_locale_insights(start_of_today, activities, entities)
    log.info(f"Collect insights for {date}: ProjectLocale insights created.")

    collect_locale_insights(start_of_today, activities, entities)
    log.info(f"Collect insights for {date}: Locale insights created.")


def collect_project_locale_insights(start_of_today, activities, entities):
    """
    Collect insights for each available ProjectLocale.
    """
    ProjectLocaleInsightsSnapshot.objects.bulk_create(
        [
            get_project_locale_insights_snapshot(
                project_locale,
                start_of_today,
                activities,
                count_entities(
                    entities,
                    locale=project_locale.locale.id,
                    project=project_locale.project.id,
                ),
            )
            for project_locale in ProjectLocale.objects.all()
        ],
        batch_size=1000,
    )


def collect_locale_insights(start_of_today, activities, entities):
    """
    Collect insights for each available Locale.
    """
    # Get data sources to retrieve insights from
    privileged_users = get_privileged_users()
    contributors = get_contributors()
    active_users_actions = get_active_users_actions(start_of_today)
    suggestions = get_suggestions()

    LocaleInsightsSnapshot.objects.bulk_create(
        [
            get_locale_insights_snapshot(
                locale,
                start_of_today,
                privileged_users[locale.id],
                contributors[locale.id],
                active_users_actions[locale.id],
                suggestions[locale.id],
                activities,
                count_entities(entities, locale=locale.id),
            )
            for locale in Locale.objects.available()
        ],
        batch_size=1000,
    )


def get_privileged_users():
    """Get managers and translators."""
    privileged_users = (
        Locale.objects.available()
        .prefetch_related("managers_group__user_set", "translators_group__user_set")
        .values(
            "pk",
            "managers_group__user__last_login",
            "managers_group__user",
            "translators_group__user",
        )
    )

    return group_dict_by(privileged_users, "pk")


def get_contributors():
    """Get all contributors without system users.

    Note that excluding system user emails in the Translation QuerySet directly is slow.
    """
    system_users = User.objects.filter(profile__system_user=True).values("pk")

    contributors = (
        Translation.objects.filter(user__isnull=False)
        .exclude(user__pk__in=system_users)
        .values("locale", "user")
        .distinct()
    )

    return group_dict_by(contributors, "locale")


def get_active_users_actions(start_of_today):
    """Get actions of the previous year, needed for the Active users charts."""
    actions = (
        ActionLog.objects.filter(
            created_at__gte=start_of_today - relativedelta(year=1),
            created_at__lt=start_of_today,
        )
        .values("action_type", "created_at", "performed_by", "translation__locale")
        .distinct()
    )

    return group_dict_by(actions, "translation__locale")


def get_suggestions():
    """Get currently unreviewed suggestions."""
    suggestions = Translation.objects.filter(
        # Make sure TranslatedResource is still enabled for the locale
        locale=F("entity__resource__translatedresources__locale"),
        approved=False,
        pretranslated=False,
        fuzzy=False,
        rejected=False,
        entity__obsolete=False,
        entity__resource__project__disabled=False,
        entity__resource__project__system_project=False,
        entity__resource__project__visibility="public",
    ).values("locale", "date")

    return group_dict_by(suggestions, "locale")


def query_entities(start_of_today):
    """Get entities created on the previous day."""
    return (
        Entity.objects.filter(
            date_created__gte=start_of_today - relativedelta(days=1),
            date_created__lt=start_of_today,
            obsolete=False,
            resource__project__disabled=False,
            resource__project__system_project=False,
            resource__project__visibility="public",
        )
        .distinct()
        .values(
            locale=F("resource__translatedresources__locale"),
            project=F("resource__project"),
        )
        .annotate(count=Count("*"))
    )


def count_entities(entities, project=None, locale=None):
    """Count the number of entities (i.e. source strings) with the given project and/or locale."""
    count = 0
    for ent in entities:
        if (project is None or project == ent["project"]) and (
            locale is None or locale == ent["locale"]
        ):
            count += ent["count"]
    return count


def get_locale_insights_snapshot(
    locale,
    start_of_today,
    privileged_users,
    contributors,
    active_users_actions,
    suggestions,
    activities,
    entities_count,
):
    """Create LocaleInsightsSnapshot instance for the given locale and day using given data."""
    all_managers, all_reviewers = get_privileged_users_data(privileged_users)
    all_contributors = {c["user"] for c in contributors}

    total_managers = len(all_managers)
    total_reviewers = len(all_reviewers)
    total_contributors = len(all_contributors)

    active_users_last_month = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=1,
    )
    active_users_last_3_months = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=3,
    )
    active_users_last_6_months = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=6,
    )
    active_users_last_12_months = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=12,
    )

    unreviewed_suggestions_lifespan = get_unreviewed_suggestions_lifespan_data(
        suggestions
    )

    time_to_review_suggestions = get_time_to_review_data(
        "suggestions", activities, locale=locale.id
    )
    time_to_review_pretranslations = get_time_to_review_data(
        "pretranslations", activities, locale=locale.id
    )

    (
        human_translations,
        machinery_translations,
        new_suggestions,
        peer_approved,
        self_approved,
        rejected,
        pretranslations_chrf_score,
        pretranslations_approved,
        pretranslations_rejected,
        pretranslations_new,
    ) = get_activity_charts_data(activities, locale=locale.id)

    return LocaleInsightsSnapshot(
        locale=locale,
        created_at=start_of_today,
        # AggregatedStats
        total_strings=locale.total_strings,
        approved_strings=locale.approved_strings,
        pretranslated_strings=locale.pretranslated_strings,
        strings_with_errors=locale.strings_with_errors,
        strings_with_warnings=locale.strings_with_warnings,
        unreviewed_strings=locale.unreviewed_strings,
        # Active users
        total_managers=total_managers,
        total_reviewers=total_reviewers,
        total_contributors=total_contributors,
        active_users_last_month=active_users_last_month,
        active_users_last_3_months=active_users_last_3_months,
        active_users_last_6_months=active_users_last_6_months,
        active_users_last_12_months=active_users_last_12_months,
        # Unreviewed suggestions lifespan
        unreviewed_suggestions_lifespan=unreviewed_suggestions_lifespan,
        # Time to review suggestions
        time_to_review_suggestions=time_to_review_suggestions,
        # Time to review pretranslations
        time_to_review_pretranslations=time_to_review_pretranslations,
        # Translation activity
        completion=round(locale.completed_percent, 2),
        human_translations=human_translations,
        machinery_translations=machinery_translations,
        new_source_strings=entities_count,
        # Review activity
        peer_approved=peer_approved,
        self_approved=self_approved,
        rejected=rejected,
        new_suggestions=new_suggestions,
        # Pretranslation quality
        pretranslations_chrf_score=pretranslations_chrf_score,
        pretranslations_approved=pretranslations_approved,
        pretranslations_rejected=pretranslations_rejected,
        pretranslations_new=pretranslations_new,
    )


def get_project_locale_insights_snapshot(
    project_locale,
    start_of_today,
    activities,
    entities_count,
):
    """Create ProjectLocaleInsightsSnapshot instance for the given locale, project, and day using given data."""
    (
        human_translations,
        machinery_translations,
        new_suggestions,
        peer_approved,
        self_approved,
        rejected,
        pretranslations_chrf_score,
        pretranslations_approved,
        pretranslations_rejected,
        pretranslations_new,
    ) = get_activity_charts_data(
        activities, locale=project_locale.locale.id, project=project_locale.project.id
    )

    return ProjectLocaleInsightsSnapshot(
        project_locale=project_locale,
        created_at=start_of_today,
        # AggregatedStats
        total_strings=project_locale.total_strings,
        approved_strings=project_locale.approved_strings,
        pretranslated_strings=project_locale.pretranslated_strings,
        strings_with_errors=project_locale.strings_with_errors,
        strings_with_warnings=project_locale.strings_with_warnings,
        unreviewed_strings=project_locale.unreviewed_strings,
        # Translation activity
        completion=round(project_locale.completed_percent, 2),
        human_translations=human_translations,
        machinery_translations=machinery_translations,
        new_source_strings=entities_count,
        # Review activity
        peer_approved=peer_approved,
        self_approved=self_approved,
        rejected=rejected,
        new_suggestions=new_suggestions,
        # Pretranslation quality
        pretranslations_chrf_score=pretranslations_chrf_score,
        pretranslations_approved=pretranslations_approved,
        pretranslations_rejected=pretranslations_rejected,
        pretranslations_new=pretranslations_new,
    )


def get_privileged_users_data(privileged_users):
    """Get all privileged users for the Active users panel."""
    all_managers = set()
    all_reviewers = set()

    for user in privileged_users:
        manager = user["managers_group__user"]
        translator = user["translators_group__user"]

        if manager:
            all_managers.add(manager)
            all_reviewers.add(manager)
        if translator:
            all_reviewers.add(translator)

    return all_managers, all_reviewers


def get_active_users_data(
    start_of_today,
    privileged_users,
    active_users_actions,
    all_reviewers,
    all_contributors,
    months=12,
):
    """Get active user counts for the Active users panel."""
    active_managers = set()
    active_reviewers = set()
    active_contributors = set()

    # Get active managers
    for user in privileged_users:
        manager = user["managers_group__user"]
        last_login = user["managers_group__user__last_login"]

        if last_login:
            if last_login + relativedelta(months=months) > start_of_today:
                active_managers.add(manager)

    # Get active reviewers and contributors. Make sure they are included among all
    # users, otherwise we might include PMs and privileged users of other locales.
    for action in active_users_actions:
        user = action["performed_by"]
        if user in all_reviewers and action["action_type"] in (
            "translation:approved",
            "translation:unapproved",
            "translation:rejected",
            "translation:unrejected",
        ):
            if action["created_at"] + relativedelta(months=months) > start_of_today:
                active_reviewers.add(user)

        if user in all_contributors and action["action_type"] == "translation:created":
            if action["created_at"] + relativedelta(months=months) > start_of_today:
                active_contributors.add(user)

    return {
        "managers": len(active_managers),
        "reviewers": len(active_reviewers),
        "contributors": len(active_contributors),
    }


def get_unreviewed_suggestions_lifespan_data(suggestions):
    """Get average age of the unreviewed suggestion."""
    unreviewed_suggestions_lifespan = timedelta()
    suggestion_count = len(suggestions)

    if suggestion_count > 0:
        total_suggestion_age = timedelta()

        for s in suggestions:
            total_suggestion_age += timezone.now() - s["date"]

        unreviewed_suggestions_lifespan = total_suggestion_age / suggestion_count

    return unreviewed_suggestions_lifespan


def get_time_to_review_data(category, activities, locale):
    """Get average time to review a suggestion or pretranslation."""
    times_to_review = list()

    for (locale_, _), data in activities.items():
        if locale == locale_:
            times_to_review.extend(data[f"times_to_review_{category}"])

    if not times_to_review:
        return None

    times_to_review = [i for i in times_to_review if i is not None]
    return sum(times_to_review, timedelta()) / len(times_to_review)


def get_chrf_score(action, approved_translations):
    key = (action["translation__entity"], action["translation__locale"])
    try:
        approved_translation = approved_translations[key]
    except KeyError:
        return None

    score = chrfpp.sentence_score(action["translation__string"], [approved_translation])
    return float(score.format(score_only=True))


def get_approved_translations(actions, pretranslation_users):
    """Fetch approved translations of entities with rejected pretranslations, needed for
    faster chrf++ score calculation."""
    rejected_pretranslation_actions = [
        action
        for action in actions
        if action["action_type"] == "translation:rejected"
        and action["user"] in pretranslation_users
    ]

    # This will catch a superset of required approved translations, which is much more
    # convenient to capture than the exact set, but doesn't seem to impact performance.
    approved_translations = Translation.objects.filter(
        entity__in=[a["translation__entity"] for a in rejected_pretranslation_actions],
        locale__in=[a["translation__locale"] for a in rejected_pretranslation_actions],
        approved=True,
    ).values("entity", "locale", "string")

    res = {}
    for translation in approved_translations:
        key = (translation["entity"], translation["locale"])
        res[key] = translation["string"]

    return res


def query_actions(start_of_today):
    """Get actions of the previous day, needed to render charts."""
    return ActionLog.objects.filter(
        created_at__gte=start_of_today - relativedelta(days=1),
        created_at__lt=start_of_today,
        translation__entity__resource__project__system_project=False,
        translation__entity__resource__project__visibility="public",
    ).values(
        "action_type",
        "performed_by",
        "translation",
        "translation__entity",
        "translation__locale",
        "translation__string",
        machinery_sources=F("translation__machinery_sources"),
        user=F("translation__user"),
        approved_user=F("translation__approved_user"),
        date=F("translation__date"),
        approved_date=F("translation__approved_date"),
        rejected_date=F("translation__rejected_date"),
        project=F("translation__entity__resource__project"),
    )


def build_charts_data(start_of_today):
    """Fetch and prepare data needed to render charts."""
    res = dict()

    sync_user = User.objects.get(email="pontoon-sync@example.com").pk
    pretranslation_users = User.objects.filter(
        email__in=[
            "pontoon-tm@example.com",
            "pontoon-gt@example.com",
        ]
    ).values_list("pk", flat=True)

    actions = query_actions(start_of_today)
    approved_translations = get_approved_translations(actions, pretranslation_users)

    for action in actions:
        key = (action["translation__locale"], action["project"])
        if key not in res:
            res[key] = {
                "human_translations": set(),
                "machinery_translations": set(),
                "new_suggestions": set(),
                "peer_approved": set(),
                "self_approved": set(),
                "rejected": set(),
                "pretranslations_chrf_scores": list(),
                "pretranslations_approved": set(),
                "pretranslations_rejected": set(),
                "pretranslations_new": set(),
                "times_to_review_suggestions": list(),
                "times_to_review_pretranslations": list(),
            }
        data = res[key]

        action_type = action["action_type"]
        performed_by = action["performed_by"]
        translation = action["translation"]

        # Review actions performed by the sync process are ignored, because they
        # aren't explicit user review actions.
        performed_by_sync = performed_by == sync_user

        if action_type == "translation:created":
            if len(action["machinery_sources"]) == 0:
                data["human_translations"].add(translation)
            else:
                data["machinery_translations"].add(translation)

            if not action["approved_date"] or action["approved_date"] > action["date"]:
                data["new_suggestions"].add(translation)

            if action["user"] in pretranslation_users:
                data["pretranslations_new"].add(translation)

            # Self-approval can also happen on translation submission
            if performed_by == action["approved_user"] and not performed_by_sync:
                data["self_approved"].add(translation)

        elif action_type == "translation:approved" and not performed_by_sync:
            if performed_by == action["user"]:
                data["self_approved"].add(translation)
            else:
                data["peer_approved"].add(translation)
                if action["approved_date"]:
                    review_time = action["approved_date"] - action["date"]
                    data["times_to_review_suggestions"].append(review_time)
                    if action["user"] in pretranslation_users:
                        data["times_to_review_pretranslations"].append(review_time)
            if action["user"] in pretranslation_users:
                data["pretranslations_approved"].add(translation)
                # Translation has been approved, no need to claculate the chrF++ score.
                # Note that the score is assigned to the pretranslation review date
                # rather than its creation date, which would be preferable.
                data["pretranslations_chrf_scores"].append(100)

        elif action_type == "translation:rejected" and not performed_by_sync:
            data["rejected"].add(translation)
            if action["rejected_date"]:
                review_time = action["rejected_date"] - action["date"]
                data["times_to_review_suggestions"].append(review_time)
                if action["user"] in pretranslation_users:
                    data["times_to_review_pretranslations"].append(review_time)
            if action["user"] in pretranslation_users:
                data["pretranslations_rejected"].add(translation)
                score = get_chrf_score(action, approved_translations)
                if score:
                    data["pretranslations_chrf_scores"].append(score)

    return res


def get_activity_charts_data(activities, project=None, locale=None):
    """Get data for Translation activity and Review activity charts."""
    human_translations = set()
    machinery_translations = set()
    new_suggestions = set()
    peer_approved = set()
    self_approved = set()
    rejected = set()
    pretranslations_chrf_scores = list()
    pretranslations_approved = set()
    pretranslations_rejected = set()
    pretranslations_new = set()

    for (locale_, project_), data in activities.items():
        if (project is None or project == project_) and (
            locale is None or locale == locale_
        ):
            human_translations.update(data["human_translations"])
            machinery_translations.update(data["machinery_translations"])
            new_suggestions.update(data["new_suggestions"])
            peer_approved.update(data["peer_approved"])
            self_approved.update(data["self_approved"])
            rejected.update(data["rejected"])
            pretranslations_chrf_scores.extend(data["pretranslations_chrf_scores"])
            pretranslations_approved.update(data["pretranslations_approved"])
            pretranslations_rejected.update(data["pretranslations_rejected"])
            pretranslations_new.update(data["pretranslations_new"])

    scores = pretranslations_chrf_scores

    return (
        len(human_translations),
        len(machinery_translations),
        len(new_suggestions),
        len(peer_approved),
        len(self_approved),
        len(rejected),
        statistics.mean(scores) if scores else None,
        len(pretranslations_approved),
        len(pretranslations_rejected),
        len(pretranslations_new),
    )
