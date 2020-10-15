from collections import defaultdict

from django.db.models import (
    Count,
    Prefetch,
)

from pontoon.base.models import (
    Locale,
    Translation,
    User,
)


def map_translations_to_events(days, translations):
    """
    Map translations into events (jsonable dictionaries) to display them on the user timeline.
    :param QuerySet[Translation] events: a QuerySet with translastions.
    :rtype: list[dict]
    :return: A list of dicts with mapped fields.
    """
    timeline = []
    for day in days:
        daily = translations.filter(date__startswith=day["day"])
        daily.prefetch_related("entity__resource__project")
        example = daily.order_by("-pk").first()

        timeline.append(
            {
                "date": example.date,
                "type": "translation",
                "count": day["count"],
                "project": example.entity.resource.project,
                "translation": example,
            }
        )

    return timeline


def users_with_translations_counts(start_date=None, query_filters=None, limit=100):
    """
    Returns contributors list, sorted by count of their translations. Every user instance has
    the following properties:
    * translations_count
    * translations_approved_count
    * translations_rejected_count
    * translations_unapproved_count
    * translations_needs_work_count
    * user_role

    All counts will be returned from start_date to now().
    :param date start_date: start date for translations.
    :param django.db.models.Q query_filters: filters contributors by given query_filters.
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
    translations = translations.values(
        "user", "approved", "fuzzy", "rejected"
    ).annotate(count=Count("approved"))

    for translation in translations:
        count = translation["count"]
        user = translation["user"]

        if translation["approved"]:
            status = "approved"
        elif translation["fuzzy"]:
            status = "fuzzy"
        elif translation["rejected"]:
            status = "rejected"
        else:
            status = "unreviewed"

        if user not in user_stats:
            user_stats[user] = {
                "total": 0,
                "approved": 0,
                "unreviewed": 0,
                "fuzzy": 0,
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

    for locale in locales:
        for user in locale.managers_group.fetched_managers:
            managers[user].add(locale.code)
        for user in locale.translators_group.fetched_translators:
            translators[user].add(locale.code)

    # Assign properties to user objects.
    contributors = User.objects.filter(pk__in=user_stats.keys())

    # Exclude deleted users.
    contributors = contributors.filter(is_active=True)

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
        contributor.translations_needs_work_count = user["fuzzy"]

        if contributor.pk is None:
            contributor.user_role = "System User"
        else:
            contributor.user_role = contributor.role(managers, translators)

    contributors_list = sorted(contributors, key=lambda x: -x.translations_count)
    if limit:
        contributors_list = contributors_list[:limit]

    return contributors_list
