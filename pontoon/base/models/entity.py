from collections.abc import Iterable
from functools import reduce
from operator import ior
from re import escape, match

from dirtyfields import DirtyFieldsMixin

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Prefetch, Q
from django.utils import timezone

from pontoon.base import utils
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.base.models.section import Section


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


class EntityQuerySet(models.QuerySet):
    def _get_query(self, locale: Locale, project: Project | None, query: Q) -> Q:
        from pontoon.base.models.translation import Translation

        translations = Translation.objects.filter(locale=locale).filter(query)
        if project and project.slug != "all-projects":
            translations = translations.filter(entity__resource__project=project)
        return Q(pk__in=translations.values("entity"))

    def missing(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities marked as "missing".

        An entity is marked as "missing" if it has no approved or pretranslated translations.
        """
        return ~self._get_query(
            locale, project, Q(approved=True) | Q(pretranslated=True)
        )

    def warnings(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities with approved, pretranslated or fuzzy translations with warnings.
        """
        return self._get_query(
            locale,
            project,
            (Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
            & Q(warnings__isnull=False),
        )

    def errors(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities with approved, pretranslated or fuzzy translations with errors.
        """
        return self._get_query(
            locale,
            project,
            (Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
            & Q(errors__isnull=False),
        )

    def pretranslated(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities marked as "pretranslated", with no errors or warnings.
        """
        return self._get_query(
            locale,
            project,
            Q(pretranslated=True, warnings__isnull=True, errors__isnull=True),
        )

    def translated(self, locale: Locale, project: Project | None) -> Q:
        """
        Return a filter for entities marked as "approved", with no errors or warnings.
        """
        return self._get_query(
            locale,
            project,
            Q(approved=True, warnings__isnull=True, errors__isnull=True),
        )

    def unreviewed(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities with suggested translations.

        An entity is said to have suggestions if it has at least one unreviewed suggestion
        (not approved, not rejected, not pretranslated, not fuzzy).
        """
        return self._get_query(
            locale,
            project,
            Q(approved=False, rejected=False, pretranslated=False, fuzzy=False),
        )

    def rejected(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities with rejected translations.
        """
        return self._get_query(locale, project, Q(rejected=True))

    def missing_without_unreviewed(
        self, locale: Locale, project: Project | None = None
    ) -> Q:
        """
        Return a filter for entities with no translations or only rejected translations.
        """
        return ~self._get_query(
            locale,
            project,
            Q(approved=True) | Q(pretranslated=True) | Q(rejected=False),
        )

    def fuzzy(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities marked as "fuzzy".
        """
        return self._get_query(
            locale, project, Q(fuzzy=True, warnings__isnull=True, errors__isnull=True)
        )

    def empty(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities with empty translations.
        """
        return self._get_query(locale, project, Q(string=""))

    def unchanged(self, locale: Locale, project: Project | None = None) -> Q:
        """
        Return a filter for entities that have unchanged translations.

        An entity is "unchanged" if its translation is equal to the source string.
        """
        return self._get_query(
            locale, project, Q(active=True, string=F("entity__string"))
        )

    def authored_by(self, locale, emails):
        # Validate if user passed a real email
        sanitized_emails = filter(utils.is_email, emails)
        query = Q()

        if sanitized_emails:
            query |= Q(translation__user__email__in=sanitized_emails)

        if "imported" in emails:
            query |= Q(translation__user__isnull=True)

        if sanitized_emails or "imported" in emails:
            return query & Q(translation__locale=locale)

        return Q()

    def reviewed_by(self, locale, emails):
        # Validate if user passed a real email
        sanitized_emails = filter(utils.is_email, emails)

        if sanitized_emails:
            return Q(translation__locale=locale) & (
                Q(translation__approved_user__email__in=sanitized_emails)
                | Q(translation__rejected_user__email__in=sanitized_emails)
            )

        return Q()

    def between_time_interval(self, locale, start, end):
        return Q(translation__locale=locale, translation__date__range=(start, end))

    def between_review_time_interval(self, locale, start, end):
        return Q(
            Q(translation__locale=locale)
            & (
                Q(translation__approved_date__range=(start, end))
                | Q(translation__rejected_date__range=(start, end))
            )
        )

    def prefetch_entities_data(self, locale: Locale, preferred_source_locale: str):
        # Prefetch active translations for given locale
        from pontoon.base.models.translation import Translation

        # Prefetch related Translations, Section comments, and ProjectLocales
        entities = (
            self.prefetch_related(
                Prefetch(
                    "translation_set",
                    queryset=(
                        Translation.objects.filter(
                            locale=locale, active=True
                        ).prefetch_related("errors", "warnings")
                    ),
                    to_attr="active_translations",
                )
            )
            .annotate(
                section_comment=models.Subquery(
                    Section.objects.filter(id=models.OuterRef("section_id")).values(
                        "comment"
                    )
                )
            )
            .prefetch_related(
                Prefetch(
                    "resource__project__project_locale",
                    queryset=ProjectLocale.objects.filter(locale=locale),
                    to_attr="projectlocale",
                )
            )
        )

        # Prefetch approved translations for given preferred source locale
        if preferred_source_locale != "":
            entities = entities.prefetch_related(
                Prefetch(
                    "translation_set",
                    queryset=(
                        Translation.objects.filter(
                            locale__code=preferred_source_locale, approved=True
                        )
                    ),
                    to_attr="alternative_originals",
                )
            )

        return entities


class Entity(DirtyFieldsMixin, models.Model):
    resource = models.ForeignKey(Resource, models.CASCADE, related_name="entities")
    section = models.ForeignKey(
        Section, models.SET_NULL, related_name="entities", null=True, blank=True
    )
    string = models.TextField()
    key = ArrayField(models.TextField(), default=list)
    value = models.JSONField(default=list)
    properties = models.JSONField(null=True, blank=True)
    meta = ArrayField(ArrayField(models.TextField(), size=2), default=list)
    comment = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    obsolete = models.BooleanField(default=False)

    date_created = models.DateTimeField(default=timezone.now)
    date_obsoleted = models.DateTimeField(null=True, blank=True)

    changed_locales = models.ManyToManyField(
        Locale,
        through="ChangedEntityLocale",
        help_text="List of locales in which translations for this entity have "
        "changed since the last sync.",
    )
    objects = EntityQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["resource", "obsolete"])]

    def __str__(self):
        return self.string

    def get_stats(self, locale) -> dict[str, int]:
        """
        Get stats for a single (entity, locale) pair.

        :arg Locale locale: filter translations for this locale.
        :return: a dictionary with stats for the Entity+Locale
        """
        approved = 0
        pretranslated = 0
        errors = 0
        warnings = 0
        unreviewed = 0

        for t in self.translation_set.filter(locale=locale).prefetch_related(
            "errors", "warnings"
        ):
            if t.errors.exists():
                if t.approved or t.pretranslated or t.fuzzy:
                    errors += 1
            elif t.warnings.exists():
                if t.approved or t.pretranslated or t.fuzzy:
                    warnings += 1
            elif t.approved:
                approved += 1
            elif t.pretranslated:
                pretranslated += 1
            if not (t.approved or t.pretranslated or t.fuzzy or t.rejected):
                unreviewed += 1

        return {
            "approved": approved,
            "pretranslated": pretranslated,
            "errors": errors,
            "warnings": warnings,
            "unreviewed": unreviewed,
        }

    def has_changed(self, locale):
        """
        Check if translations in the given locale have changed since the
        last sync.
        """
        return locale in self.changed_locales.all()

    def reset_active_translation(self, locale: Locale):
        """
        Reset active translation for given entity and locale.
        Return active translation if exists or empty Translation instance.
        """
        from pontoon.base.models.translation import Translation

        translations = self.translation_set.filter(locale=locale)
        translations.update(active=False)

        candidates = translations.filter(rejected=False).order_by(
            "-approved", "-pretranslated", "-fuzzy", "-date"
        )

        if candidates:
            active_translation = candidates[0]
            active_translation.active = True

            # Do not trigger the overridden Translation.save() method
            super(Translation, active_translation).save(update_fields=["active"])

            return active_translation
        else:
            return Translation()

    def reset_term_translation(self, locale):
        """
        When translation in the "Terminology" project changes, update the corresponding
        TermTranslation:
        - If approved translation exists, use it as TermTranslation
        - If approved translation doesn't exist, remove any TermTranslation instance

        This method is also executed in the process of deleting a term translation,
        because it needs to be rejected first, which triggers the call to this
        function.
        """
        from pontoon.base.models.translation import Translation

        term = self.term

        try:
            approved_translation = self.translation_set.get(
                locale=locale, approved=True
            )
            term_translation, _ = term.translations.get_or_create(locale=locale)
            term_translation.text = approved_translation.string
            term_translation.save(update_fields=["text"])
        except Translation.DoesNotExist:
            term.translations.filter(locale=locale).delete()

    @classmethod
    def for_project_locale(
        self,
        user,
        project,
        locale,
        paths=None,
        status=None,
        tag=None,
        search=None,
        extra=None,
        search_identifiers=None,
        search_exclude_source_strings=None,
        search_rejected_translations=None,
        search_match_case=None,
        search_match_whole_word=None,
        time=None,
        author=None,
        review_time=None,
        reviewer=None,
        exclude_self_reviewed=None,
    ):
        """Get project entities with locale translations."""

        # Time & author filters have to be applied before the aggregation
        # (with_status_counts) and the status & extra filters to avoid
        # unnecessary joins causing performance and logic issues.
        pre_filters = []
        post_filters = []

        if time:
            if match("^[0-9]{12}-[0-9]{12}$", time):
                start, end = utils.parse_time_interval(time)
                pre_filters.append(
                    Entity.objects.between_time_interval(locale, start, end)
                )

        if review_time:
            if match("^[0-9]{12}-[0-9]{12}$", review_time):
                start, end = utils.parse_time_interval(review_time)
                pre_filters.append(
                    Entity.objects.between_review_time_interval(locale, start, end)
                )

        if author:
            pre_filters.append(Entity.objects.authored_by(locale, author.split(",")))

        if reviewer:
            pre_filters.append(Entity.objects.reviewed_by(locale, reviewer.split(",")))

        if exclude_self_reviewed:
            pre_filters.append(
                ~Q(
                    Q(translation__approved_user=F("translation__user"))
                    | Q(translation__rejected_user=F("translation__user"))
                )
            )

        entities: EntityQuerySet
        if pre_filters:
            entities = Entity.objects.filter(
                pk__in=Entity.objects.filter(Q(*pre_filters))
            )
        else:
            entities = Entity.objects.all()

        entities = entities.filter(
            resource__translatedresources__locale=locale,
            resource__project__disabled=False,
            obsolete=False,
        )

        if project.slug == "all-projects":
            visible_projects = Project.objects.visible_for(user)
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
            search_list = utils.get_search_phrases(search)

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
                & (
                    Q()
                    if search_rejected_translations
                    else Q(translation__rejected=False)
                )
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

            entity_matches = entities.filter(*entity_filters).values_list(
                "id", flat=True
            )

            entities = Entity.objects.filter(
                pk__in=set(list(translation_matches) + list(entity_matches))
            )

        order_fields = ("resource__order", "order")
        if project.slug == "all-projects":
            order_fields = ("resource__project__name",) + order_fields

        return entities.order_by(*order_fields)

    @classmethod
    def map_entities(
        cls,
        locale: Locale,
        preferred_source_locale,
        entities: EntityQuerySet,
        is_sibling: bool = False,
        requested_entity: int | None = None,
    ):
        entities_: Iterable[Entity] = entities.prefetch_entities_data(
            locale, preferred_source_locale
        )

        # If requested entity not in the current page
        if requested_entity and requested_entity not in [e.pk for e in entities_]:
            entities_ = list(entities_) + list(
                Entity.objects.filter(pk=requested_entity).prefetch_entities_data(
                    locale, preferred_source_locale
                )
            )

        entities_array = []
        for entity in entities_:
            try:
                readonly = entity.resource.project.projectlocale[0].readonly
            except IndexError:
                # Entities explicitly requested using `string` or `list` URL parameters
                # might not be enabled for localization for the given locale. If the
                # project is given in the URL, the 404 page shows up, but if the All
                # Projects view is used, we hit the IndexError here, because the
                # `projectlocale` list is empty. In this case, we skip the entity.
                continue

            if preferred_source_locale != "" and entity.alternative_originals:
                original = entity.alternative_originals[0].string
            else:
                original = entity.string

            translation = (
                entity.active_translations[0].serialize()
                if entity.active_translations
                else None
            )

            entities_array.append(
                {
                    "pk": entity.pk,
                    "original": original,
                    "machinery_original": entity.string,
                    "key": entity.key,
                    "path": entity.resource.path,
                    "project": entity.resource.project.serialize(),
                    "format": entity.resource.format,
                    "comment": entity.comment,
                    "group_comment": entity.section_comment or "",
                    "resource_comment": entity.resource.comment or "",
                    "meta": entity.meta,
                    "obsolete": entity.obsolete,
                    "translation": translation,
                    "readonly": readonly,
                    "is_sibling": is_sibling,
                    "date_created": entity.date_created,
                }
            )

        return entities_array
