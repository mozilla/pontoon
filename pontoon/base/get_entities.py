from datetime import datetime, timedelta, timezone
from re import escape, match
from typing import Iterator, cast

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import F, Q
from django.utils.timezone import make_aware

from pontoon.base.models import Entity, Locale, Project, Resource, Translation, User
from pontoon.base.models.entity import EntityQuerySet
from pontoon.base.models.project import ProjectQuerySet
from pontoon.base.utils import get_search_phrases


def get_entities_for_project_locale(
    user: User,
    project: Project,
    locale: Locale,
    paths: list[str] | None = None,
    status: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    extra: str | None = None,
    search_identifiers: bool = False,
    search_exclude_source_strings: bool = False,
    search_rejected_translations: bool = False,
    search_match_case: bool = False,
    search_match_whole_word: bool = False,
    time: str | None = None,
    created_time: str | None = None,
    author: str | None = None,
    review_time: str | None = None,
    reviewer: str | None = None,
    exclude_self_reviewed: bool = False,
) -> EntityQuerySet:
    """Get project entities with locale translations."""

    entities = cast(EntityQuerySet, Entity.objects)

    pre_filter = Q(
        *_time_and_user_filters(
            locale,
            time,
            created_time,
            review_time,
            author,
            reviewer,
            exclude_self_reviewed,
        )
    )
    if pre_filter:
        # Time & user filters have to be applied before the aggregation
        # (with_status_counts) and the status & extra filters to avoid
        # unnecessary joins causing performance and logic issues.
        entities = entities.filter(pk__in=Entity.objects.filter(pre_filter))

    entities = entities.filter(
        resource__translatedresources__locale=locale,
        resource__project__disabled=False,
        obsolete=False,
    )

    if project.slug == "all-projects":
        visible_projects = cast(ProjectQuerySet, Project.objects).visible_for(user)
        entities = entities.filter(
            resource__project__system_project=False,
            resource__project__in=visible_projects,
        )
    else:
        entities = entities.filter(resource__project=project)

    if paths:
        entities = entities.filter(resource__path__in=paths)

    post_filter = Q()

    if status and (status_query := _status_filter(project, locale, status)):
        post_filter &= status_query

    if extra and (extra_query := _extra_filter(locale, extra)):
        post_filter &= extra_query

    if tag:
        post_filter &= Q(resource__tag__slug__in=tag.split(","))

    if post_filter:
        entities = entities.filter(post_filter)
        if tag:
            # only tag needs `distinct` as it traverses m2m fields
            entities = entities.distinct()

    # Filter by search parameters
    if search:
        search_list = get_search_phrases(search)

        # Modify query based on case & match sensitivity filters
        i = "" if search_match_case else "i"
        y = r"\y" if search_match_whole_word else ""

        # Use regex to ignore context identifiers by default
        r = "" if search_identifiers else "=.*"
        o = "" if search_identifiers else ".*"

        translation_filters = (
            (
                Q(
                    Q(resource__format=Resource.Format.FLUENT)
                    & (
                        Q(
                            **{
                                f"translation__string__{i}regex": rf"{r}{y}{escape(s)}{y}{o}"
                            }
                        )
                    )
                )
                | Q(
                    ~Q(resource__format=Resource.Format.FLUENT)
                    & Q(**{f"translation__string__{i}regex": rf"{y}{escape(s)}{y}"})
                )
            )
            & Q(translation__locale=locale)
            & (Q() if search_rejected_translations else Q(translation__rejected=False))
            for s in search_list
        )

        translation_matches = entities.filter(*translation_filters).values_list(
            "id", flat=True
        )

        # Search in source strings
        entity_filters = (
            (
                Q(pk__in=[])  # Ensures that no source strings are returned
                if search_exclude_source_strings
                else (
                    Q(
                        Q(resource__format=Resource.Format.FLUENT)
                        & (Q(**{f"string__{i}regex": rf"{r}{y}{escape(s)}{y}{o}"}))
                    )
                    | Q(
                        ~Q(resource__format=Resource.Format.FLUENT)
                        & Q(**{f"string__{i}regex": rf"{y}{escape(s)}{y}"})
                    )
                )
            )
            | (
                Q(**{f"key__{i}regex": rf"{y}{escape(s)}{y}"})
                if search_identifiers
                else Q()
            )
            for s in search_list
        )

        entity_matches = entities.filter(*entity_filters).values_list("id", flat=True)

        entities = cast(EntityQuerySet, Entity.objects).filter(
            pk__in=set(list(translation_matches) + list(entity_matches))
        )

    order_fields: tuple[str, ...] = ("resource__order", "order")
    if project.slug == "all-projects":
        order_fields = ("resource__project__name",) + order_fields

    return entities.order_by(*order_fields)


def _time_and_user_filters(
    locale: Locale,
    time: str | None,
    created_time: str | None,
    review_time: str | None,
    author: str | None,
    reviewer: str | None,
    exclude_self_reviewed: bool,
) -> Iterator[Q]:
    if time and match("^[0-9]{12}-[0-9]{12}$", time):
        range = _parse_time_interval(time)
        yield Q(translation__locale=locale, translation__date__range=range)

    if created_time and match("^[0-9]{12}-[0-9]{12}$", created_time):
        range = _parse_time_interval(created_time)
        yield Q(date_created__range=range)

    if review_time and match("^[0-9]{12}-[0-9]{12}$", review_time):
        range = _parse_time_interval(review_time)
        yield Q(translation__locale=locale) & (
            Q(translation__approved_date__range=range)
            | Q(translation__rejected_date__range=range)
        )

    if author:
        emails = author.split(",")
        query = Q(translation__user__isnull=True) if "imported" in emails else Q()

        emails = [e for e in emails if _is_email(e)]
        if emails:
            query |= Q(translation__user__email__in=emails)
        if query:
            yield query & Q(translation__locale=locale)

    if reviewer:
        emails = [e for e in reviewer.split(",") if _is_email(e)]
        if emails:
            yield Q(translation__locale=locale) & (
                Q(translation__approved_user__email__in=emails)
                | Q(translation__rejected_user__email__in=emails)
            )

    if exclude_self_reviewed:
        yield ~Q(
            Q(translation__approved_user=F("translation__user"))
            | Q(translation__rejected_user=F("translation__user"))
        )


def _parse_time_interval(interval: str) -> tuple[datetime, datetime]:
    """
    Return start and end time objects from time interval string in the format
    %d%m%Y%H%M-%d%m%Y%H%M. Also, increase interval by one minute due to
    truncation to a minute in Translation.counts_per_minute QuerySet.
    """

    start, end = interval.split("-")

    return _parse_timestamp(start), _parse_timestamp(end) + timedelta(minutes=1)


def _parse_timestamp(timestamp: str) -> datetime:
    return make_aware(datetime.strptime(timestamp, "%Y%m%d%H%M"), timezone=timezone.utc)


def _is_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def _status_filter(project: Project, locale: Locale, status: str) -> Q:
    """Apply a combination of filters based on the list of statuses the user sent."""
    query = Q()
    for s in status.split(","):
        match s:
            case "warnings":
                q = (Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True)) & Q(
                    warnings__isnull=False
                )
            case "errors":
                q = (Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True)) & Q(
                    errors__isnull=False
                )
            case "pretranslated":
                q = Q(pretranslated=True, warnings__isnull=True, errors__isnull=True)
            case "translated":
                q = Q(approved=True, warnings__isnull=True, errors__isnull=True)
            case "unreviewed":
                q = Q(approved=False, rejected=False, pretranslated=False, fuzzy=False)
            case "missing":
                q = Q(approved=True) | Q(pretranslated=True)
                query |= ~_query(project, locale, q)
                continue
            case _:
                continue
        query |= _query(project, locale, q)
    return query


def _extra_filter(locale: Locale, extra: str) -> Q:
    """Apply a combination of filters based on the list of extras the user sent."""
    query = Q()
    for e in extra.split(","):
        match e:
            case "rejected":
                q = Q(rejected=True)
            case "unchanged":
                q = Q(active=True, string=F("entity__string"))
            case "empty":
                q = Q(string="")
            case "fuzzy":
                q = Q(fuzzy=True, warnings__isnull=True, errors__isnull=True)
            case "missing-without-unreviewed":
                q = Q(approved=True) | Q(pretranslated=True) | Q(rejected=False)
                query |= ~_query(None, locale, q)
                continue
            case _:
                continue
        query |= _query(None, locale, q)
    return query


def _query(project: Project | None, locale: Locale, query: Q) -> Q:
    translations = Translation.objects.filter(locale=locale).filter(query)
    if project and project.slug != "all-projects":
        translations = translations.filter(entity__resource__project=project)
    return Q(pk__in=translations.values("entity"))
