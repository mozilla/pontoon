import datetime

from collections import defaultdict
from typing import Literal, cast
from urllib.parse import urlencode

import jwt

from allauth.socialaccount.models import SocialAccount
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db.models import (
    Count,
    F,
    Prefetch,
    Q,
)
from django.db.models.functions import TruncDay, TruncMonth
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone

from pontoon.actionlog.models import ActionLog, ActionLogQuerySet
from pontoon.base.models import (
    Locale,
    Translation,
    User,
    UserBanLog,
)
from pontoon.base.templatetags.helpers import intcomma
from pontoon.base.user_utils import user_locale_role, user_role
from pontoon.base.utils import convert_to_unix_time


def users_with_translations_counts(
    start_date=None, query_filters=None, locale=None, limit=None
):
    """
    Returns contributors list, sorted by count of their translations. Every user instance has
    the following properties:
    * translations_count
    * translations_approved_count
    * translations_rejected_count
    * translations_unapproved_count
    * user_role

    All counts will be returned from start_date to now().
    :param date start_date: start date for translations.
    :param django.db.models.Q query_filters: filters contributors by given query_filters.
    :param pontoon.base.models.Locale locale: used to determine user locale role.
    :param int limit: limit results to this number.
    """
    # Collect data for faster user stats calculation.
    user_stats = {}
    translations = Translation.objects.all()

    if start_date:
        translations = translations.filter(date__gte=start_date)

    if query_filters:
        translations = translations.filter(query_filters)

    # Count('user') returns 0 if the user is None.
    # See https://docs.djangoproject.com/en/1.11/topics/db/aggregation/#values.
    translations = translations.values("user", "approved", "rejected").annotate(
        count=Count("approved")
    )

    for translation in translations:
        count = translation["count"]
        user = translation["user"]

        if translation["approved"]:
            status = "approved"
        elif translation["rejected"]:
            status = "rejected"
        else:
            status = "unreviewed"

        if user not in user_stats:
            user_stats[user] = {
                "total": 0,
                "approved": 0,
                "unreviewed": 0,
                "rejected": 0,
            }

        user_stats[user]["total"] += count
        user_stats[user][status] += count

    # Collect data for faster user role detection.
    managers = defaultdict(set)
    translators = defaultdict(set)

    locales = Locale.objects.prefetch_related(
        Prefetch("managers_group__user_set", to_attr="fetched_managers"),
        Prefetch("translators_group__user_set", to_attr="fetched_translators"),
    )

    for loc in locales:
        for user in loc.managers_group.fetched_managers:
            managers[user].add(loc.code)
        for user in loc.translators_group.fetched_translators:
            translators[user].add(loc.code)

    contributors = (
        User.objects.filter(
            pk__in=user_stats.keys(),
            is_active=True,
        )
        .prefetch_related("profile")
        .prefetch_related(
            Prefetch(
                "socialaccount_set",
                queryset=SocialAccount.objects.filter(provider="fxa"),
                to_attr="_prefetched_fxa_accounts",
            )
        )
    )

    if None in user_stats.keys():
        contributors = list(contributors)
        contributors.append(
            User(username="Imported", first_name="Imported", email="imported")
        )

    # Assign properties to user objects.
    for contributor in contributors:
        user = user_stats[contributor.pk]
        contributor.translations_count = user["total"]
        contributor.translations_approved_count = user["approved"]
        contributor.translations_rejected_count = user["rejected"]
        contributor.translations_unapproved_count = user["unreviewed"]

        contributor.user_role = user_role(contributor, managers, translators)

        if locale:
            contributor.user_locale_role = user_locale_role(contributor, locale)

    contributors_list = sorted(contributors, key=lambda x: -x.translations_count)
    if limit:
        contributors_list = contributors_list[:limit]

    return contributors_list


def generate_verification_token(user):
    payload = {
        "user": user.pk,
        "email": user.profile.contact_email,
        "exp": timezone.now() + relativedelta(hours=1),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def check_verification_token(user, token):
    profile = user.profile
    title = "Oops!"

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")

        if payload["user"] == user.pk and payload["email"] == profile.contact_email:
            profile.contact_email_verified = True
            profile.save(update_fields=["contact_email_verified"])

            title = "Success!"
            message = "Your email address has been verified"

        else:
            raise jwt.exceptions.InvalidTokenError

    except jwt.exceptions.ExpiredSignatureError:
        message = "Verification token has expired"

    except jwt.exceptions.InvalidTokenError:
        message = "Invalid verification token"

    return title, message


def get_n_months_before(start, n):
    """
    Get a list of first days of the last n months before the given time
    """
    return sorted(
        [
            convert_to_unix_time(
                datetime.date(start.year, start.month, 1) - relativedelta(months=i)
            )
            for i in range(n)
        ]
    )


def get_monthly_action_counts(months, actions_qs):
    """
    Get a list of counts of given actions within each month given by the list of months.
    """
    values = [0] * len(months)

    for item in (
        actions_qs.annotate(created_month=TruncMonth("created_at"))
        .values("created_month")
        .annotate(count=Count("id"))
        .values("created_month", "count")
    ):
        date = convert_to_unix_time(item["created_month"])
        index = months.index(date)
        values[index] = item["count"]

    return values


def get_shares_of_totals(list1, list2):
    """
    Get a list of shares of items from the first list in the sum of items from
    both lists at the same position.
    """
    return [
        0 if sum(pair) == 0 else (pair[0] / sum(pair) * 100)
        for pair in zip(list1, list2)
    ]


def get_12_month_sums(lst):
    """
    Get a list of 12-month sums.
    """
    return [sum(lst[x : x + 12]) for x in range(12)]


def get_12_month_averages(list1, list2):
    """
    Get a list of 12-month averages.
    """
    return get_shares_of_totals(get_12_month_sums(list1), get_12_month_sums(list2))


def get_approvals_charts_data(user):
    """
    Get data required to render Approval rate charts on the Profile page
    """
    months = get_n_months_before(timezone.now(), 23)

    actions = ActionLog.objects.filter(
        created_at__gte=timezone.now() - relativedelta(months=22),
        translation__user=user,
    )

    peer_actions = actions.exclude(performed_by=user)
    peer_approvals = get_monthly_action_counts(
        months,
        peer_actions.filter(action_type=ActionLog.ActionType.TRANSLATION_APPROVED),
    )
    peer_rejections = get_monthly_action_counts(
        months,
        peer_actions.filter(action_type=ActionLog.ActionType.TRANSLATION_REJECTED),
    )

    self_actions = actions.filter(performed_by=user)
    self_approvals = get_monthly_action_counts(
        months,
        self_actions.filter(
            # Self-approved after submitting as a suggestion.
            # Exclude implicit approvals, which are logged alongside the
            # `translation:created` action for translations submitted directly
            # as approved (counted via the branch below).
            Q(
                action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
                is_implicit_action=False,
            )
            # Submitted directly as translations
            | Q(
                action_type=ActionLog.ActionType.TRANSLATION_CREATED,
                translation__date=F("translation__approved_date"),
            )
        ),
    )

    approval_rates = get_shares_of_totals(peer_approvals, peer_rejections)
    approval_rates_12_month_avg = get_12_month_averages(peer_approvals, peer_rejections)
    self_approval_rates = get_shares_of_totals(self_approvals, peer_approvals)
    self_approval_rates_12_month_avg = get_12_month_averages(
        self_approvals, peer_approvals
    )

    return {
        "dates": months[-12:],
        "approval_rates": approval_rates[-12:],
        "approval_rates_12_month_avg": approval_rates_12_month_avg,
        "self_approval_rates": self_approval_rates[-12:],
        "self_approval_rates_12_month_avg": self_approval_rates_12_month_avg,
    }


def get_contributions_map(
    contributor: User, viewer: User, contribution_period: Q | None = None
):
    """
    Return a map of contribution types and corresponding QuerySets of contributions.

    :param django.db.models.Q contribution_period: ActionLog time interval.
    """

    actions_base = cast(ActionLogQuerySet, ActionLog.objects)
    actions = actions_base.visible_for(viewer)

    if contribution_period is not None:
        actions = actions.filter(contribution_period, is_implicit_action=False)

    review_action_types = [
        ActionLog.ActionType.TRANSLATION_APPROVED,
        ActionLog.ActionType.TRANSLATION_REJECTED,
    ]

    user_translations = actions.filter(
        performed_by=contributor, action_type=ActionLog.ActionType.TRANSLATION_CREATED
    )
    user_reviews = actions.filter(
        performed_by=contributor, action_type__in=review_action_types
    )
    peer_reviews = actions.filter(
        translation__user=contributor, action_type__in=review_action_types
    )

    all_user_contributions = user_translations | user_reviews

    # Using the union of all_user_contributions and peer_reviews QuerySets results in poorer performance
    all_contributions = actions_base.filter(
        pk__in=(
            list(all_user_contributions.values_list("pk", flat=True))
            + list(peer_reviews.values_list("pk", flat=True))
        )
    )

    return {
        "user_translations": user_translations,
        "user_reviews": user_reviews,
        "peer_reviews": peer_reviews,
        "all_user_contributions": all_user_contributions,
        "all_contributions": all_contributions,
    }


def get_contribution_graph_data(
    contributor: User,
    viewer: User,
    contribution_type: str | None = None,
    year: int | None = None,
):
    """
    Get data required to render the Contribution graph on the Profile page.

    Returned data covers the requested `year`, or the last 12 months if
    `year` is None.
    """

    if year is None:
        contribution_period = Q(
            created_at__gte=timezone.now() - relativedelta(days=365)
        )
        period_label = "in the last year"
    else:
        start = timezone.make_aware(timezone.datetime(year, 1, 1))
        end = start + relativedelta(years=1)
        contribution_period = Q(created_at__gte=start, created_at__lt=end)
        period_label = f"in {year}"

    contributions_map = get_contributions_map(contributor, viewer, contribution_period)

    if contribution_type is None or contribution_type not in contributions_map.keys():
        contribution_type = "all_user_contributions"

    contributions_qs = contributions_map[contribution_type]
    contributions_data: dict[int, int] = {
        convert_to_unix_time(item["timestamp"]): item["count"]
        for item in (
            contributions_qs.annotate(timestamp=TruncDay("created_at"))
            .values("timestamp")
            .annotate(count=Count("id"))
            .values("timestamp", "count")
        )
    }

    total = sum(contributions_data.values())

    return (
        contributions_data,
        f"{intcomma(total)} contribution{pluralize(total)} {period_label}",
    )


def get_contribution_years(contributor: User):
    """
    Return the list of calendar years to offer in the contribution graph,
    from the current year back to the year the contributor joined.
    """
    current_year = timezone.now().year
    first_year = contributor.date_joined.year
    return list(range(current_year, first_year - 1, -1))


def get_project_locale_contribution_counts(contributions_qs: ActionLogQuerySet):
    counts = {}

    for item in (
        contributions_qs.annotate(
            month=TruncMonth("created_at"),
            project_name=F("translation__entity__resource__project__name"),
            project_slug=F("translation__entity__resource__project__slug"),
            locale_name=F("translation__locale__name"),
            locale_code=F("translation__locale__code"),
        )
        .values("month", "project_name", "project_slug", "locale_name", "locale_code")
        .annotate(count=Count("id"))
        .values(
            "month",
            "project_name",
            "project_slug",
            "locale_name",
            "locale_code",
            "action_type",
            "count",
        )
    ):
        month = item["month"].strftime("%B %Y")
        key = (item["project_slug"], item["locale_code"])
        count = item["count"]

        match item["action_type"]:
            case "translation:created":
                action = f"{intcomma(count)} translation{pluralize(count)}"
            case "translation:approved":
                action = f"{intcomma(count)} approved"
            case "translation:rejected" | _:
                action = f"{intcomma(count)} rejected"

        if month not in counts:
            counts[month] = {}

        if key in counts[month]:
            counts[month][key]["actions"].append(action)
            counts[month][key]["count"] += count
        else:
            counts[month][key] = {
                "project": {
                    "name": item["project_name"],
                    "slug": item["project_slug"],
                },
                "locale": {
                    "name": item["locale_name"],
                    "code": item["locale_code"],
                },
                "actions": [action],
                "count": count,
                "url": "",
            }

    return counts


def get_contribution_timeline_data(
    contributor, viewer, full_year=False, contribution_type=None, day=None, year=None
):
    """
    Get data required to render the Contribution timeline on the Profile page
    """
    end = timezone.now()

    if year is not None:
        # Limit data to the selected calendar year, up to now for the current year
        year_start = timezone.make_aware(timezone.datetime(year, 1, 1))
        end = min(end, year_start + relativedelta(years=1))
        if full_year:
            # Get data for the whole year
            start = year_start
        else:
            # Get data for the most recent month within the year
            start = (end - relativedelta(seconds=1)).replace(day=1)
    elif full_year:
        # Get data from the 1st day of the current month, one year ago, to now
        start = end - relativedelta(years=1, day=1)
    else:
        # Get data from the 1st day of the current month to now
        start = end - relativedelta(day=1)

    # Set start to be 00:00 (midnight)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    if day is not None:
        start = datetime.datetime.fromtimestamp(day, tz=timezone.get_current_timezone())
        end = start + relativedelta(days=1)

    contribution_period = Q(created_at__gte=start, created_at__lte=end)
    contributions_map = get_contributions_map(contributor, viewer, contribution_period)

    # Get a list of explicit contribution types
    contribution_types: list[
        Literal["user_translations", "user_reviews", "peer_reviews"]
    ]
    match contribution_type:
        case "user_translations" | "user_reviews" | "peer_reviews":
            contribution_types = [contribution_type]
        case "all_contributions":
            contribution_types = ["user_translations", "user_reviews", "peer_reviews"]
        case "all_user_contributions" | _:
            contribution_types = ["user_translations", "user_reviews"]

    start_ = start.strftime("%Y%m%d%H%M")
    end_ = end.strftime("%Y%m%d%H%M")
    time_str = f"{start_}-{end_}"

    contributions = {}
    for contribution_type in contribution_types:
        contributions_qs = contributions_map[contribution_type]
        contribution_data = get_project_locale_contribution_counts(contributions_qs)

        for month, data in contribution_data.items():
            total_count = sum([info["count"] for _, info in data.items()])
            p_count = len(data)

            # Generate title for the localizations belonging to the same contribution type
            match contribution_type:
                case "user_translations":
                    title = f"Submitted {intcomma(total_count)} translation{pluralize(total_count)}"
                    url_params = {
                        "author": contributor.email,
                        "time": time_str,
                    }
                case "user_reviews":
                    title = f"Reviewed {intcomma(total_count)} suggestion{pluralize(total_count)}"
                    url_params = {
                        "reviewer": contributor.email,
                        "review_time": time_str,
                    }
                case "peer_reviews":
                    title = f"Received review for {intcomma(total_count)} suggestion{pluralize(total_count)}"
                    url_params = {
                        "author": contributor.email,
                        "review_time": time_str,
                        "exclude_self_reviewed": "",
                    }
            title += f" in {intcomma(p_count)} project{pluralize(p_count)}"

            # Generate localization URL and add it to the data dict
            for _, val in data.items():
                url = reverse(
                    "pontoon.translate",
                    args=[
                        val["locale"]["code"],
                        val["project"]["slug"],
                        "all-resources",
                    ],
                )
                val["url"] = f"{url}?{urlencode(url_params)}"

                if month not in contributions:
                    contributions[month] = {}

                if contribution_type not in contributions[month]:
                    contributions[month][contribution_type] = {}

                contributions[month][contribution_type].update(
                    {
                        "data": data,
                        "type": contribution_type.replace("_", "-"),
                        "title": title,
                    }
                )

    # Sort contributions in reverse-chronological order
    sorted_contributions = dict(
        sorted(
            contributions.items(),
            key=lambda item: datetime.datetime.strptime(item[0], "%B %Y"),
            reverse=True,
        )
    )

    return sorted_contributions


def log_user_ban(actor, target, reason):
    action_type = (
        UserBanLog.ActionType.UNBANNED
        if target.is_active
        else UserBanLog.ActionType.BANNED
    )
    UserBanLog.objects.create(
        performed_by=actor,
        performed_on=target,
        action_reason=reason,
        action_type=action_type,
    )
