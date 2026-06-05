from functools import reduce
from operator import ior
from re import escape, match
from typing import cast

from django.db.models import F, Q

from pontoon.base.models import Entity, Locale, Project, Resource, User
from pontoon.base.models.entity import EntityQuerySet
from pontoon.base.models.project import ProjectQuerySet
from pontoon.base.utils import get_search_phrases, parse_time_interval


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

    # Time & author filters have to be applied before the aggregation
    # (with_status_counts) and the status & extra filters to avoid
    # unnecessary joins causing performance and logic issues.
    pre_filters = []
    post_filters = []

    entity_objects = cast(EntityQuerySet, Entity.objects)
    if time:
        if match("^[0-9]{12}-[0-9]{12}$", time):
            start, end = parse_time_interval(time)
            pre_filters.append(entity_objects.between_time_interval(locale, start, end))

    if created_time:
        if match("^[0-9]{12}-[0-9]{12}$", created_time):
            start, end = parse_time_interval(created_time)
            pre_filters.append(entity_objects.between_created_time_interval(start, end))

    if review_time:
        if match("^[0-9]{12}-[0-9]{12}$", review_time):
            start, end = parse_time_interval(review_time)
            pre_filters.append(
                entity_objects.between_review_time_interval(locale, start, end)
            )

    if author:
        pre_filters.append(entity_objects.authored_by(locale, author.split(",")))

    if reviewer:
        pre_filters.append(entity_objects.reviewed_by(locale, reviewer.split(",")))

    if exclude_self_reviewed:
        pre_filters.append(
            ~Q(
                Q(translation__approved_user=F("translation__user"))
                | Q(translation__rejected_user=F("translation__user"))
            )
        )

    if pre_filters:
        entities = entity_objects.filter(pk__in=Entity.objects.filter(Q(*pre_filters)))
    else:
        entities = entity_objects.all()

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

    # Filter by path
    if paths:
        entities = entities.filter(resource__path__in=paths)

    if status:
        # Apply a combination of filters based on the list of statuses the user sent.
        status_filter_choices = (
            "missing",
            "warnings",
            "errors",
            "pretranslated",
            "translated",
            "unreviewed",
        )
        post_filters.append(
            combine_entity_filters(
                entities, status_filter_choices, status.split(","), locale, project
            )
        )

    if extra:
        # Apply a combination of filters based on the list of extras the user sent.
        extra_filter_choices = (
            "rejected",
            "unchanged",
            "empty",
            "fuzzy",
            "missing-without-unreviewed",
        )
        post_filters.append(
            combine_entity_filters(
                entities, extra_filter_choices, extra.split(","), locale
            )
        )

    if tag:
        post_filters.append(Q(resource__tag__slug__in=tag.split(",")))

    if post_filters:
        entities = entities.filter(Q(*post_filters))
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

        entities = Entity.objects.filter(
            pk__in=set(list(translation_matches) + list(entity_matches))
        )

    order_fields: tuple[str, ...] = ("resource__order", "order")
    if project.slug == "all-projects":
        order_fields = ("resource__project__name",) + order_fields

    return entities.order_by(*order_fields)


def combine_entity_filters(entities, filter_choices, filters, *args):
    """Return a combination of filters to apply to an Entity object.

    The content for each filter is defined in the EntityQuerySet helper class, using methods
    that have the same name as the filter. Each subset of filters is combined with the others
    with the OR operator.

    :arg EntityQuerySet entities: an Entity query set object with predefined filters
    :arg list filter_choices: list of valid choices, used to sanitize the content of `filters`
    :arg list filters: the filters to get and combine
    :arg *args: arguments that will be passed to the filter methods of the EntityQuerySet class

    :returns: a combination of django ORM Q() objects containing all the required filters

    """
    # We first sanitize the list sent by the user and restrict it to only values we accept.
    sanitized_filters = filter(lambda s: s in filter_choices, filters)

    filters = [Q()]
    for filter_name in sanitized_filters:
        filters.append(getattr(entities, filter_name.replace("-", "_"))(*args))

    # Combine all generated filters with an OR operator.
    # `operator.ior` is the pipe (|) Python operator, which turns into a logical OR
    # when used between django ORM query objects.
    return reduce(ior, filters)
