from functools import reduce
from operator import ior
from re import findall, match

from dirtyfields import DirtyFieldsMixin
from jsonfield import JSONField

from django.db import models
from django.db.models import F, Prefetch, Q
from django.utils import timezone

from pontoon.base import utils
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.sync import KEY_SEPARATOR


def get_word_count(string):
    """Compute the number of words in a given string."""
    return len(findall(r"[\w,.-]+", string))


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
    def get_filtered_entities(
        self, locale, query, rule, project=None, match_all=True, prefetch=None
    ):
        """Return a QuerySet of values of entity PKs matching the locale, query and rule.

        Filter entities that match the given filter provided by the `locale` and `query`
        parameters. For performance reasons the `rule` parameter is also provided to filter
        entities in python instead of the DB.

        :arg Locale locale: a Locale object to get translations for
        :arg Q query: a django ORM Q() object describing translations to filter
        :arg function rule: a lambda function implementing the `query` logic
        :arg boolean match_all: if true, all plural forms must match the rule.
            Otherwise, only one matching is enough
        :arg prefetch django.db.models.Prefetch prefetch: if set, it's used to control the
            operation of prefetch_related() on the query.

        :returns: a QuerySet of values of entity PKs

        """
        from pontoon.base.models.translation import Translation

        # First, separately filter entities with plurals (for performance reasons)
        plural_pks = []

        if locale.nplurals:
            # For each entity with plurals, fetch translations matching the query.
            plural_candidates = self.exclude(string_plural="").prefetch_related(
                Prefetch(
                    "translation_set",
                    queryset=(
                        Translation.objects.filter(locale=locale)
                        .filter(query)
                        .prefetch_related(prefetch)
                    ),
                    to_attr="fetched_translations",
                )
            )

            # Walk through the plural forms one by one and check that:
            #  - they have a translation
            #  - the translation matches the rule
            for candidate in plural_candidates:
                count = 0
                for i in range(locale.nplurals):
                    candidate_translations = [
                        translation
                        for translation in candidate.fetched_translations
                        if translation.plural_form == i
                    ]
                    if len(candidate_translations) and rule(candidate_translations[0]):
                        count += 1

                        # No point going on if we don't care about matching all.
                        if not match_all:
                            continue

                # If `match_all` is True, we want all plural forms to have a match.
                # Otherwise, just one of them matching is enough.
                if (match_all and count == locale.nplurals) or (
                    not match_all and count
                ):
                    plural_pks.append(candidate.pk)

        translations = Translation.objects.filter(locale=locale)

        # Additional filter on the project field speeds things up because it makes faster
        # to execute a SQL subquery generated by Django.
        if project and project.slug != "all-projects":
            translations = translations.filter(entity__resource__project=project)

        # Finally, we return a query that returns both the matching entities with no
        # plurals and the entities with plurals that were stored earlier.
        return translations.filter(
            Q(Q(entity__string_plural="") & query) | Q(entity_id__in=plural_pks)
        ).values("entity")

    def missing(self, locale, project=None):
        """Return a filter to be used to select entities marked as "missing".

        An entity is marked as "missing" if at least one of its plural forms
        has no approved or pretranslated translations.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return ~Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(approved=True) | Q(pretranslated=True),
                lambda x: x.approved or x.pretranslated,
                project=project,
            )
        )

    def warnings(self, locale, project=None):
        """Return a filter to be used to select entities with translations with warnings.

        This filter will return an entity if at least one of its plural forms
        has an approved, pretranslated or fuzzy translation with a warning.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                (Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                & Q(warnings__isnull=False),
                lambda x: (x.approved or x.pretranslated or x.fuzzy)
                and x.warnings.count(),
                match_all=False,
                prefetch=Prefetch("warnings"),
                project=project,
            )
        )

    def errors(self, locale, project=None):
        """Return a filter to be used to select entities with translations with errors.

        This filter will return an entity if at least one of its plural forms
        has an approved, pretranslated or fuzzy translation with an error.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                (Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                & Q(errors__isnull=False),
                lambda x: (x.approved or x.pretranslated or x.fuzzy)
                and x.errors.count(),
                match_all=False,
                prefetch=Prefetch("errors"),
                project=project,
            )
        )

    def pretranslated(self, locale, project=None):
        """Return a filter to be used to select entities marked as "pretranslated".

        An entity is marked as "pretranslated" if all of its plural forms have a pretranslated translation.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(pretranslated=True, warnings__isnull=True, errors__isnull=True),
                lambda x: x.pretranslated,
                project=project,
            )
        )

    def translated(self, locale, project):
        """Return a filter to be used to select entities marked as "approved".

        An entity is marked as "approved" if all of its plural forms have an approved translation.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(approved=True, warnings__isnull=True, errors__isnull=True),
                lambda x: x.approved,
                project=project,
            )
        )

    def unreviewed(self, locale, project=None):
        """Return a filter to be used to select entities with suggested translations.

        An entity is said to have suggestions if at least one of its plural forms
        has at least one unreviewed suggestion (not approved, not rejected, not pretranslated, not fuzzy).

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(approved=False, rejected=False, pretranslated=False, fuzzy=False),
                lambda x: not x.approved
                and not x.rejected
                and not x.pretranslated
                and not x.fuzzy,
                match_all=False,
                project=project,
            )
        )

    def rejected(self, locale, project=None):
        """Return a filter to be used to select entities with rejected translations.

        This filter will return all entities that have a rejected translation.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(rejected=True),
                lambda x: x.rejected,
                match_all=False,
                project=project,
            )
        )

    def missing_without_unreviewed(self, locale, project=None):
        """Return a filter to be used to select entities with no or only rejected translations.

        This filter will return all entities that have no or only rejected translations.
        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return ~Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(approved=True) | Q(pretranslated=True) | Q(rejected=False),
                lambda x: x.approved or x.pretranslated or not x.rejected,
                project=project,
            )
        )

    def fuzzy(self, locale, project=None):
        """Return a filter to be used to select entities marked as "fuzzy".

        An entity is marked as "fuzzy" if all of its plural forms have a fuzzy
        translation.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(fuzzy=True, warnings__isnull=True, errors__isnull=True),
                lambda x: x.fuzzy,
                project=project,
            )
        )

    def empty(self, locale, project=None):
        """Return a filter to be used to select empty translations.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(string=""),
                lambda x: x.string == "",
                match_all=False,
                project=project,
            )
        )

    def unchanged(self, locale, project=None):
        """Return a filter to be used to select entities that have unchanged translations.

        An entity is marked as "unchanged" if all of its plural forms have translations
        equal to the source string.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(active=True)
                & (
                    Q(string=F("entity__string")) | Q(string=F("entity__string_plural"))
                ),
                lambda x: x.active
                and (x.string == x.entity.string or x.string == x.entity.string_plural),
                match_all=False,
                project=project,
            )
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

    def prefetch_entities_data(self, locale, preferred_source_locale):
        # Prefetch active translations for given locale
        from pontoon.base.models.translation import Translation

        entities = self.prefetch_related(
            Prefetch(
                "translation_set",
                queryset=(
                    Translation.objects.filter(
                        locale=locale, active=True
                    ).prefetch_related(
                        "errors",
                        "warnings",
                    )
                ),
                to_attr="active_translations",
            )
        )

        # Prefetch related Translations, Resources, Projects and ProjectLocales
        entities = entities.prefetch_related(
            Prefetch(
                "resource__project__project_locale",
                queryset=ProjectLocale.objects.filter(locale=locale),
                to_attr="projectlocale",
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

    def reset_active_translations(self, locale):
        """
        Reset active translation for given set of entities and locale.
        """
        from pontoon.base.models.translation import Translation

        translations = Translation.objects.filter(
            entity__in=self,
            locale=locale,
        )

        # First, deactivate all translations
        translations.update(active=False)

        # Mark all approved, pretranslated and fuzzy translations as active.
        translations.filter(
            Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True)
        ).update(active=True)

        # Mark most recent unreviewed suggestions without active siblings
        # for any given combination of (locale, entity, plural_form) as active.
        unreviewed_pks = set()
        unreviewed = translations.filter(
            approved=False,
            pretranslated=False,
            fuzzy=False,
            rejected=False,
        ).values_list("entity", "plural_form")

        for entity, plural_form in unreviewed:
            siblings = (
                Translation.objects.filter(
                    entity=entity,
                    locale=locale,
                    plural_form=plural_form,
                )
                .exclude(rejected=True)
                .order_by("-active", "-date")
            )
            if siblings and not siblings[0].active:
                unreviewed_pks.add(siblings[0].pk)

        translations.filter(pk__in=unreviewed_pks).update(active=True)

    def get_or_create(self, defaults=None, **kwargs):
        kwargs["word_count"] = get_word_count(kwargs["string"])
        return super().get_or_create(defaults=defaults, **kwargs)

    def bulk_update(self, objs, fields, batch_size=None):
        if "string" in fields:
            for obj in objs:
                obj.word_count = get_word_count(obj.string)
            if "word_count" not in fields:
                fields.append("word_count")
        super().bulk_update(objs, fields=fields, batch_size=batch_size)


class Entity(DirtyFieldsMixin, models.Model):
    resource = models.ForeignKey(Resource, models.CASCADE, related_name="entities")
    string = models.TextField()
    string_plural = models.TextField(blank=True)
    # Unique identifier, used to compare DB and VCS objects
    key = models.TextField()
    # Format-specific value, used to provide more context
    context = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    group_comment = models.TextField(blank=True)
    resource_comment = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    source = JSONField(blank=True, default=list)  # List of paths to source code files
    obsolete = models.BooleanField(default=False)
    word_count = models.PositiveIntegerField(default=0)

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
        indexes = [
            models.Index(fields=["resource", "obsolete", "string_plural"]),
        ]

    @property
    def cleaned_key(self):
        """
        Get cleaned key, without the source string and Translate Toolkit
        separator.
        """
        key = self.key.split(KEY_SEPARATOR)[0]
        if key == self.string:
            key = ""

        return key

    def __str__(self):
        return self.string

    def save(self, *args, **kwargs):
        self.word_count = get_word_count(self.string)
        super().save(*args, **kwargs)

    def get_stats(self, locale):
        """
        Get stats for a single (entity, locale) pair.

        :arg Locale locale: filter translations for this locale.
        :return: a dictionary with stats for an Entity, all keys are suffixed with `_diff` to
            make them easier to pass into adjust_all_stats.
        """
        translations = list(
            self.translation_set.filter(locale=locale).prefetch_related(
                "errors",
                "warnings",
            )
        )

        approved_strings_count = len(
            [
                t
                for t in translations
                if t.approved and not (t.errors.exists() or t.warnings.exists())
            ]
        )

        pretranslated_strings_count = len(
            [
                t
                for t in translations
                if t.pretranslated and not (t.errors.exists() or t.warnings.exists())
            ]
        )

        if self.string_plural:
            approved = int(approved_strings_count == locale.nplurals)
            pretranslated = int(pretranslated_strings_count == locale.nplurals)

        else:
            approved = int(approved_strings_count > 0)
            pretranslated = int(pretranslated_strings_count > 0)

        if not (approved or pretranslated):
            has_errors = bool(
                [
                    t
                    for t in translations
                    if (t.approved or t.pretranslated or t.fuzzy) and t.errors.exists()
                ]
            )
            has_warnings = bool(
                [
                    t
                    for t in translations
                    if (t.approved or t.pretranslated or t.fuzzy)
                    and t.warnings.exists()
                ]
            )

            errors = int(has_errors)
            warnings = int(has_warnings)

        else:
            errors = 0
            warnings = 0

        unreviewed_count = len(
            [
                t
                for t in translations
                if not (t.approved or t.pretranslated or t.fuzzy or t.rejected)
            ]
        )

        return {
            "total_strings_diff": 0,
            "approved_strings_diff": approved,
            "pretranslated_strings_diff": pretranslated,
            "strings_with_errors_diff": errors,
            "strings_with_warnings_diff": warnings,
            "unreviewed_strings_diff": unreviewed_count,
        }

    @classmethod
    def get_stats_diff(cls, stats_before, stats_after):
        """
        Return stat difference between the two states of the entity.

        :arg dict stats_before: dict returned by get_stats() for the initial state.
        :arg dict stats_after: dict returned by get_stats() for the current state.
        :return: dictionary with differences between provided stats.
        """
        return {
            stat_name: stats_after[stat_name] - stats_before[stat_name]
            for stat_name in stats_before
        }

    def has_changed(self, locale):
        """
        Check if translations in the given locale have changed since the
        last sync.
        """
        return locale in self.changed_locales.all()

    def get_active_translation(self, plural_form=None):
        """
        Get active translation for a given entity and plural form.
        Active translations must be prefetched for the requested locale.
        """
        from pontoon.base.models.translation import Translation

        translations = self.active_translations

        if plural_form is not None:
            translations = [t for t in translations if t.plural_form == plural_form]

        return translations[0] if translations else Translation()

    def reset_active_translation(self, locale, plural_form=None):
        """
        Reset active translation for given entity, locale and plural form.
        Return active translation if exists or empty Translation instance.
        """
        from pontoon.base.models.translation import Translation

        translations = self.translation_set.filter(locale=locale)

        if plural_form is not None:
            translations = translations.filter(plural_form=plural_form)

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

            translation_filters = (
                Q(translation__string__icontains_collate=(search, locale.db_collation))
                & Q(translation__locale=locale)
                for search in search_list
            )

            translation_matches = entities.filter(*translation_filters).values_list(
                "id", flat=True
            )

            q_key = Q(key__icontains=search)  # if search_identifiers else Q()
            entity_filters = (
                Q(string__icontains=search) | Q(string_plural__icontains=search) | q_key
                for search in search_list
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
        locale,
        preferred_source_locale,
        entities,
        is_sibling=False,
        requested_entity=None,
    ):
        entities_array = []

        entities = entities.prefetch_entities_data(locale, preferred_source_locale)

        # If requested entity not in the current page
        if requested_entity and requested_entity not in [e.pk for e in entities]:
            entities = list(entities) + list(
                Entity.objects.filter(pk=requested_entity).prefetch_entities_data(
                    locale, preferred_source_locale
                )
            )

        for entity in entities:
            translation_array = []

            original = entity.string
            original_plural = entity.string_plural

            if original_plural == "":
                translation = entity.get_active_translation().serialize()
                translation_array.append(translation)
            else:
                for plural_form in range(0, locale.nplurals or 1):
                    translation = entity.get_active_translation(plural_form).serialize()
                    translation_array.append(translation)

            if preferred_source_locale != "" and entity.alternative_originals:
                original = entity.alternative_originals[0].string
                if original_plural != "":
                    original_plural = entity.alternative_originals[-1].string

            entities_array.append(
                {
                    "pk": entity.pk,
                    "original": original,
                    "original_plural": original_plural,
                    "machinery_original": entity.string,
                    "key": entity.cleaned_key,
                    "context": entity.context,
                    "path": entity.resource.path,
                    "project": entity.resource.project.serialize(),
                    "format": entity.resource.format,
                    "comment": entity.comment,
                    "group_comment": entity.group_comment,
                    "resource_comment": entity.resource_comment,
                    "order": entity.order,
                    "source": entity.source,
                    "obsolete": entity.obsolete,
                    "translation": translation_array,
                    "readonly": entity.resource.project.projectlocale[0].readonly,
                    "is_sibling": is_sibling,
                    "date_created": entity.date_created,
                }
            )

        return entities_array
