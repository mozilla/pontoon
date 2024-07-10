import datetime

from collections import defaultdict
from urllib.parse import urlencode

import jwt

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models import (
    Count,
    F,
    Prefetch,
    Q,
)
from django.db.models.functions import TruncDay, TruncMonth
from django.template.defaultfilters import pluralize
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    Locale,
    Translation,
)
from pontoon.base.templatetags.helpers import format_datetime, intcomma
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

    # Assign properties to user objects.
    contributors = User.objects.filter(pk__in=user_stats.keys())

    # Exclude deleted users.
    contributors = contributors.filter(is_active=True)

    # Prefetch user profile.
    contributors = contributors.prefetch_related("profile")

    if None in user_stats.keys():
        contributors = list(contributors)
        contributors.append(
            User(username="Imported", first_name="Imported", email="imported")
        )

    for contributor in contributors:
        user = user_stats[contributor.pk]
        contributor.translations_count = user["total"]
        contributor.translations_approved_count = user["approved"]
        contributor.translations_rejected_count = user["rejected"]
        contributor.translations_unapproved_count = user["unreviewed"]

        contributor.user_role = contributor.role(managers, translators)

        if locale:
            contributor.user_locale_role = contributor.locale_role(locale)

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


def send_verification_email(request, token):
    template = get_template("contributors/verification_email.jinja")
    mail_subject = "Verify Email Address for Pontoon"

    link = request.build_absolute_uri(
        reverse("pontoon.contributors.verify.email", args=(token,))
    )
    mail_body = template.render(
        {
            "display_name": request.user.display_name,
            "link": link,
        }
    )

    EmailMessage(
        subject=mail_subject,
        body=mail_body,
        to=[request.user.profile.contact_email],
    ).send()


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
            # Self-approved after submitting suggestions
            Q(action_type=ActionLog.ActionType.TRANSLATION_APPROVED)
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


def get_contributions_map(user, contribution_period=None):
    """
    Return a map of contribution types and corresponding QuerySets of contributions.

    :param django.db.models.Q contribution_period: ActionLog time interval.
    """
    actions = ActionLog.objects.all()

    if contribution_period is not None:
        actions = actions.filter(contribution_period)

    review_action_types = [
        ActionLog.ActionType.TRANSLATION_APPROVED,
        ActionLog.ActionType.TRANSLATION_REJECTED,
    ]

    user_translations = actions.filter(
        performed_by=user, action_type=ActionLog.ActionType.TRANSLATION_CREATED
    )
    user_reviews = actions.filter(
        performed_by=user, action_type__in=review_action_types
    )
    peer_reviews = actions.filter(
        translation__user=user, action_type__in=review_action_types
    )

    all_user_contributions = user_translations | user_reviews

    # Using the union of all_user_contributions and peer_reviews QuerySets results in poorer performance
    all_contributions = ActionLog.objects.filter(
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


def get_contribution_graph_data(user, contribution_type=None):
    """
    Get data required to render the Contribution graph on the Profile page
    """
    contribution_period = Q(created_at__gte=timezone.now() - relativedelta(days=365))
    contributions_map = get_contributions_map(user, contribution_period)

    if contribution_type not in contributions_map.keys():
        contribution_type = "all_user_contributions"

    contributions_qs = contributions_map[contribution_type]
    contributions_data = {
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
        f"{ intcomma(total) } contribution{ pluralize(total) } in the last year",
    )


def get_project_locale_contribution_counts(contributions_qs):
    counts = {}

    for item in (
        contributions_qs.annotate(
            project_name=F("translation__entity__resource__project__name"),
            project_slug=F("translation__entity__resource__project__slug"),
            locale_name=F("translation__locale__name"),
            locale_code=F("translation__locale__code"),
            translation_created_date=F("translation__date"),
            translation_rejected_date=F("translation__rejected_date"),
            translation_approved_date=F("translation__approved_date"),
        )
        .values(
            "project_name",
            "project_slug",
            "locale_name",
            "locale_code",
            "translation_created_date",
            "translation_rejected_date",
            "translation_approved_date",
        )
        .annotate(
            count=Count("id"),
        )
        .values(
            "project_name",
            "project_slug",
            "locale_name",
            "locale_code",
            "translation_created_date",
            "translation_rejected_date",
            "translation_approved_date",
            "action_type",
            "count",
        )
    ):
        key = (item["project_slug"], item["locale_code"])
        count = item["count"]

        date = None
        if item["action_type"] == "translation:created":
            action = f"{ intcomma(count) } translation{ pluralize(count) }"
            date = item.get("translation_created_date")
            if date:
                date = date.strftime("%B %Y")
        elif item["action_type"] == "translation:approved":
            action = f"{ intcomma(count) } approved"
            date = item.get("translation_approved_date")
            if date:
                date = date.strftime("%B %Y")
            else:
                date = "January 1970"
        elif item["action_type"] == "translation:rejected":
            action = f"{ intcomma(count) } rejected"
            date = item.get("translation_rejected_date")
            if date:
                date = date.strftime("%B %Y")
            else:
                date = "January 1970"

        if key in counts.keys():
            counts[key]["action_dates"].append({"action": action, "date": date})
            counts[key]["count"] += count

        else:
            counts[key] = {
                "project": {
                    "name": item["project_name"],
                    "slug": item["project_slug"],
                },
                "locale": {
                    "name": item["locale_name"],
                    "code": item["locale_code"],
                },
                "action_dates": [
                    {
                        "action": action,
                        "date": date,
                    }
                ],
                "count": count,
            }
    return counts


def get_monthly_timeline_titles(contributions):
    """
    Regenerate titles and counts for each month and contribution_type
    """
    for date, types in contributions.items():
        for contribution_type, entries in types.items():
            c_count = sum(entry["count"] for entry in entries)
            print(entries, c_count)
            p_count = len(entries)

            if contribution_type == "user-translations":
                title = f"Submitted { intcomma(c_count) } translation{ pluralize(c_count) } in { intcomma(p_count) } project{ pluralize(p_count) }"
            elif contribution_type == "user-reviews":
                title = f"Reviewed { intcomma(c_count) } suggestion{ pluralize(c_count) } in { intcomma(p_count) } project{ pluralize(p_count) }"
            elif contribution_type == "peer-reviews":
                title = f"Received review for { intcomma(c_count) } suggestion{ pluralize(c_count) } in { intcomma(p_count) } project{ pluralize(p_count) }"

            contributions[date][contribution_type] = {
                "title": title,
                "entries": entries,
            }

    return contributions


def combine_actions(actions_list):
    """
    Combine print statements for identical actions in the same project and month
    """
    combined = defaultdict(int)
    total_count = 0
    for action in actions_list:
        parts = action.split()
        count = int(parts[0])
        action_type = " ".join(parts[1:])
        combined[action_type] += count
        total_count += count

    combined_actions = []
    for action_type, count in combined.items():
        if "translation" in action_type:
            action = f"{count} translation{ pluralize(count) }"
        else:
            action = f"{count} {action_type}"
        combined_actions.append(action)

    return combined_actions, total_count


def get_contribution_timeline_data(
    user, year_shown=False, contribution_type=None, day=None
):
    """
    Get data required to render the Contribution timeline on the Profile page
    """
    end = timezone.now()

    if year_shown:
        start = end - relativedelta(years=1, day=1)
        timeline_title = "Contribution activity in the last year"
    else:
        start = end - relativedelta(day=1)
        timeline_title = "Contribution activity in this month"

    if day is not None:
        start = datetime.datetime.fromtimestamp(day, tz=timezone.get_current_timezone())
        end = start + relativedelta(days=1)
        date = format_datetime(start, format="date")
        timeline_title = f"Contribution activity on { date }"

    contribution_period = Q(created_at__gte=start, created_at__lte=end)
    contributions_map = get_contributions_map(user, contribution_period)

    # Get a list of explicit contribution types
    default_contribution_types = ["user_translations", "user_reviews"]
    if contribution_type not in contributions_map.keys():
        contribution_types = default_contribution_types
    elif contribution_type == "all_user_contributions":
        contribution_types = default_contribution_types
    elif contribution_type == "all_contributions":
        contribution_types = default_contribution_types + ["peer_reviews"]
    else:
        contribution_types = [contribution_type]

    start_ = start.strftime("%Y%m%d%H%M")
    end_ = end.strftime("%Y%m%d%H%M")
    params_map = {
        "user_translations": {
            "author": user.email,
            "time": f"{ start_ }-{ end_ }",
        },
        "user_reviews": {
            "reviewer": user.email,
            "review_time": f"{ start_ }-{ end_ }",
        },
        "peer_reviews": {
            "author": user.email,
            "review_time": f"{ start_ }-{ end_ }",
            "exclude_self_reviewed": "",
        },
    }

    contributions = {}
    for contribution_type in contribution_types:
        contributions_qs = contributions_map[contribution_type]
        contribution_data = get_project_locale_contribution_counts(contributions_qs)

        c_count = sum([value["count"] for _, value in contribution_data.items()])
        p_count = len(contribution_data)

        if c_count == 0:
            continue

        # Generate localizaton URL and add it to the data dict
        params = params_map[contribution_type]
        for key, val in contribution_data.items():
            url = reverse(
                "pontoon.translate",
                args=[val["locale"]["code"], val["project"]["slug"], "all-resources"],
            )
            contribution_data[key]["url"] = f"{url}?{urlencode(params)}"

        # Generate title for the localizations belonging to the same contribution type
        if contribution_type == "user_translations":
            title = f"Submitted { intcomma(c_count) } translation{ pluralize(c_count) } in { intcomma(p_count) } project{ pluralize(p_count) }"
        elif contribution_type == "user_reviews":
            title = f"Reviewed { intcomma(c_count) } suggestion{ pluralize(c_count) } in { intcomma(p_count) } project{ pluralize(p_count) }"
        elif contribution_type == "peer_reviews":
            title = f"Received review for { intcomma(c_count) } suggestion{ pluralize(c_count) } in { intcomma(p_count) } project{ pluralize(p_count) }"

        contributions.update(
            {
                title: {
                    "data": contribution_data,
                    "type": contribution_type.replace("_", "-"),
                }
            }
        )

    if year_shown:
        # Organize return object by month
        restructured = defaultdict(lambda: defaultdict(list))
        for entry in contributions.values():
            contribution_type = entry["type"]
            for key, value in entry["data"].items():
                for action_date in value["action_dates"]:
                    date = action_date["date"]
                    action_entry = {
                        "project": value["project"],
                        "locale": value["locale"],
                        "actions": [action_date["action"]],
                        "count": value["count"],
                        "url": value["url"],
                    }
                    # Search if entry already exists. If not, create new entry
                    found = False
                    for existing_entry in restructured[date][contribution_type]:
                        if (
                            existing_entry["project"] == action_entry["project"]
                            and existing_entry["locale"] == action_entry["locale"]
                            and existing_entry["url"] == action_entry["url"]
                        ):
                            existing_entry["actions"].extend(action_entry["actions"])
                            existing_entry["actions"], count = combine_actions(
                                existing_entry["actions"]
                            )
                            existing_entry["count"] = count
                            found = True
                            break

                    if not found:
                        restructured[date][contribution_type].append(action_entry)

        restructured = get_monthly_timeline_titles(restructured)

        # Sort timeline data in reverse-chronological order
        sorted_restructured = dict(
            sorted(
                restructured.items(),
                key=lambda item: datetime.datetime.strptime(item[0], "%B %Y"),
                reverse=True,
            )
        )

        return (sorted_restructured, timeline_title, year_shown)
    else:
        # Combine similar actions for displaying
        for entry in contributions.values():
            for key, value in entry["data"].items():
                actions_list = []
                for action_date in value["action_dates"]:
                    actions_list.append(action_date["action"])
                value["action_dates"], _ = combine_actions(actions_list)

    return (
        contributions,
        timeline_title,
        year_shown,
    )
