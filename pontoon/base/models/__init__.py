import math
import operator
import re

import Levenshtein

from dirtyfields import DirtyFieldsMixin
from django.db.models.functions import Length, Substr, Cast
from functools import reduce
from django.contrib.postgres.fields import ArrayField

from django.db import models
from django.db.models import (
    Count,
    F,
    Prefetch,
    Q,
    Sum,
    Case,
    When,
    Value,
    ExpressionWrapper,
)
from django.utils import timezone

from jsonfield import JSONField
from pontoon.actionlog.models import ActionLog
from pontoon.actionlog.utils import log_action
from pontoon.base import utils
from pontoon.base.fluent import get_simple_preview
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.base.models.comment import Comment
from pontoon.base.models.aggregated_stats import AggregatedStats
from pontoon.base.models.locale import Locale, LocaleCodeHistory, validate_cldr
from pontoon.base.models.permission_changelog import PermissionChangelog
from pontoon.base.models.project import Priority, Project, ProjectSlugHistory
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.repository import Repository, repository_url_validator
from pontoon.base.models.resource import Resource
from pontoon.base.models.user import User
from pontoon.base.models.user_profile import UserProfile
from pontoon.checks import DB_FORMATS
from pontoon.checks.utils import save_failed_checks
from pontoon.db import IContainsCollate, LevenshteinDistance  # noqa
from pontoon.sync import KEY_SEPARATOR

__all__ = [
    "AggregatedStats",
    "ChangedEntityLocale",
    "Comment",
    "Entity",
    "ExternalResource",
    "Locale",
    "LocaleCodeHistory",
    "PermissionChangelog",
    "Priority",
    "Project",
    "ProjectLocale",
    "ProjectSlugHistory",
    "Repository",
    "Resource",
    "TranslatedResource",
    "Translation",
    "TranslationMemoryEntry",
    "User",
    "UserProfile",
    "get_word_count",
    "repository_url_validator",
    "validate_cldr",
]


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
    return reduce(operator.ior, filters)


def get_word_count(string):
    """Compute the number of words in a given string."""
    return len(re.findall(r"[\w,.-]+", string))


class ExternalResource(models.Model):
    """
    Represents links to external project resources like staging websites,
    production websites, development builds, production builds, screenshots,
    langpacks, etc. or team resources like style guides, dictionaries,
    glossaries, etc.
    Has no relation to the Resource class.
    """

    locale = models.ForeignKey(Locale, models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(Project, models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=32)
    url = models.URLField("URL", blank=True)

    def __str__(self):
        return self.name


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
        index_together = (("resource", "obsolete", "string_plural"),)

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
        translations = self.active_translations

        if plural_form is not None:
            translations = [t for t in translations if t.plural_form == plural_form]

        return translations[0] if translations else Translation()

    def reset_active_translation(self, locale, plural_form=None):
        """
        Reset active translation for given entity, locale and plural form.
        Return active translation if exists or empty Translation instance.
        """
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
            if re.match("^[0-9]{12}-[0-9]{12}$", time):
                start, end = utils.parse_time_interval(time)
                pre_filters.append(
                    Entity.objects.between_time_interval(locale, start, end)
                )

        if review_time:
            if re.match("^[0-9]{12}-[0-9]{12}$", review_time):
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

            entity_filters = (
                Q(string__icontains=search)
                | Q(string_plural__icontains=search)
                | Q(comment__icontains=search)
                | Q(group_comment__icontains=search)
                | Q(resource_comment__icontains=search)
                | Q(key__icontains=search)
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


class TranslationQuerySet(models.QuerySet):
    def translated_resources(self, locale):
        return TranslatedResource.objects.filter(
            resource__entities__translation__in=self, locale=locale
        ).distinct()

    def authors(self):
        """
        Return a list of translation authors.
        """
        # *Important*
        # pontoon.contributors.utils depends on a few models from pontoon.base.models and causes a
        # circular dependency.
        from pontoon.contributors.utils import users_with_translations_counts

        return [
            {
                "email": user.email,
                "display_name": user.name_or_email,
                "id": user.id,
                "gravatar_url": user.gravatar_url(88),
                "translation_count": user.translations_count,
                "role": user.user_role,
            }
            for user in users_with_translations_counts(None, Q(id__in=self))
        ]

    def counts_per_minute(self):
        """
        Return a dictionary of translation counts per minute.
        """
        translations = (
            self.extra({"minute": "date_trunc('minute', date)"})
            .order_by("minute")
            .values("minute")
            .annotate(count=Count("id"))
        )

        data = []
        for period in translations:
            data.append([utils.convert_to_unix_time(period["minute"]), period["count"]])
        return data

    def for_checks(self, only_db_formats=True):
        """
        Return an optimized queryset for `checks`-related functions.
        :arg bool only_db_formats: filter translations by formats supported by checks.
        """
        translations = self.prefetch_related(
            "entity__resource__entities",
            "locale",
        )

        if only_db_formats:
            translations = translations.filter(
                entity__resource__format__in=DB_FORMATS,
            )

        return translations

    def bulk_mark_changed(self):
        changed_entities = {}
        existing = ChangedEntityLocale.objects.values_list(
            "entity", "locale"
        ).distinct()

        for translation in self.exclude(
            entity__resource__project__data_source=Project.DataSource.DATABASE
        ):
            key = (translation.entity.pk, translation.locale.pk)

            if key not in existing:
                changed_entities[key] = ChangedEntityLocale(
                    entity=translation.entity, locale=translation.locale
                )

        ChangedEntityLocale.objects.bulk_create(changed_entities.values())


class Translation(DirtyFieldsMixin, models.Model):
    entity = models.ForeignKey(Entity, models.CASCADE)
    locale = models.ForeignKey(Locale, models.CASCADE)
    user = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    string = models.TextField()
    # Index of Locale.cldr_plurals_list()
    plural_form = models.SmallIntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    # Active translations are displayed in the string list and as the first
    # entry in the History tab. There can only be one active translation for
    # each (entity, locale, plural_form) combination. See bug 1481175.
    active = models.BooleanField(default=False)

    pretranslated = models.BooleanField(default=False)
    fuzzy = models.BooleanField(default=False)

    approved = models.BooleanField(default=False)
    approved_user = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name="approved_translations",
        null=True,
        blank=True,
    )
    approved_date = models.DateTimeField(null=True, blank=True)

    unapproved_user = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name="unapproved_translations",
        null=True,
        blank=True,
    )
    unapproved_date = models.DateTimeField(null=True, blank=True)

    rejected = models.BooleanField(default=False)
    rejected_user = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name="rejected_translations",
        null=True,
        blank=True,
    )
    rejected_date = models.DateTimeField(null=True, blank=True)

    unrejected_user = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name="unrejected_translations",
        null=True,
        blank=True,
    )
    unrejected_date = models.DateTimeField(null=True, blank=True)

    class MachinerySource(models.TextChoices):
        TRANSLATION_MEMORY = "translation-memory", "Translation Memory"
        CONCORDANCE_SEARCH = "concordance-search", "Concordance Search"
        GOOGLE_TRANSLATE = "google-translate", "Google Translate"
        MICROSOFT_TRANSLATOR = "microsoft-translator", "Microsoft Translator"
        SYSTRAN_TRANSLATE = "systran-translate", "Systran Translate"
        MICROSOFT_TERMINOLOGY = "microsoft-terminology", "Microsoft"
        CAIGHDEAN = "caighdean", "Caighdean"

    machinery_sources = ArrayField(
        models.CharField(max_length=30, choices=MachinerySource.choices),
        default=list,
        blank=True,
    )

    objects = TranslationQuerySet.as_manager()

    class Meta:
        index_together = (
            ("entity", "user", "approved", "pretranslated"),
            ("entity", "locale", "approved"),
            ("entity", "locale", "pretranslated"),
            ("entity", "locale", "fuzzy"),
            ("locale", "user", "entity"),
            ("date", "locale"),
            ("approved_date", "locale"),
        )
        constraints = [
            models.UniqueConstraint(
                name="entity_locale_plural_form_active",
                fields=["entity", "locale", "plural_form", "active"],
                condition=Q(active=True),
            ),
            # The rule above doesn't catch the plural_form = None case
            models.UniqueConstraint(
                name="entity_locale_active",
                fields=["entity", "locale", "active"],
                condition=Q(active=True, plural_form__isnull=True),
            ),
        ]

    @classmethod
    def for_locale_project_paths(self, locale, project, paths):
        """
        Return Translation QuerySet for given locale, project and paths.
        """
        translations = Translation.objects.filter(
            entity__obsolete=False, entity__resource__project=project, locale=locale
        )

        if paths:
            translations = translations.filter(entity__resource__path__in=paths)

        return translations

    @property
    def latest_activity(self):
        """
        Return the date and user associated with the latest activity on
        this translation.
        """
        if self.approved_date is not None and self.approved_date > self.date:
            return {
                "translation": self,
                "date": self.approved_date,
                "user": self.approved_user,
                "type": "approved",
            }
        else:
            return {
                "translation": self,
                "date": self.date,
                "user": self.user,
                "type": "submitted",
            }

    @property
    def machinery_sources_values(self):
        """
        Returns the corresponding comma-separated machinery_sources values
        """
        result = [
            self.MachinerySource(source).label for source in self.machinery_sources
        ]
        return ", ".join(result)

    @property
    def tm_source(self):
        source = self.entity.string

        if self.entity.resource.format == Resource.Format.FTL:
            return get_simple_preview(source)

        return source

    @property
    def tm_target(self):
        target = self.string

        if self.entity.resource.format == Resource.Format.FTL:
            return get_simple_preview(target)

        return target

    def __str__(self):
        return self.string

    def save(self, update_stats=True, failed_checks=None, *args, **kwargs):
        # We parametrize update of stats to make testing easier.
        if update_stats:
            stats_before = self.entity.get_stats(self.locale)

        super().save(*args, **kwargs)

        project = self.entity.resource.project

        # Only one translation can be approved at a time for any
        # Entity/Locale.
        if self.approved:
            approved_translations = Translation.objects.filter(
                entity=self.entity,
                locale=self.locale,
                plural_form=self.plural_form,
                rejected=False,
            ).exclude(pk=self.pk)

            # Log that all those translations are rejected.
            for t in approved_translations:
                log_action(
                    ActionLog.ActionType.TRANSLATION_REJECTED,
                    self.approved_user or self.user,
                    translation=t,
                )

            # Remove any TM entries of old translations that will get rejected.
            # Must be executed before translations set changes.
            TranslationMemoryEntry.objects.filter(
                translation__in=approved_translations
            ).delete()

            approved_translations.update(
                approved=False,
                approved_user=None,
                approved_date=None,
                rejected=True,
                rejected_user=self.approved_user,
                rejected_date=self.approved_date,
                pretranslated=False,
                fuzzy=False,
            )

            if not self.memory_entries.exists():
                TranslationMemoryEntry.objects.create(
                    source=self.tm_source,
                    target=self.tm_target,
                    entity=self.entity,
                    translation=self,
                    locale=self.locale,
                    project=project,
                )

        # Whenever a translation changes, mark the entity as having
        # changed in the appropriate locale. We could be smarter about
        # this but for now this is fine.
        if self.approved:
            self.mark_changed()

        if project.slug == "terminology":
            self.entity.reset_term_translation(self.locale)

        # We use get_or_create() instead of just get() to make it easier to test.
        translatedresource, _ = TranslatedResource.objects.get_or_create(
            resource=self.entity.resource, locale=self.locale
        )

        # Update latest translation where necessary
        self.update_latest_translation()

        # Failed checks must be saved before stats are updated (bug 1521606)
        if failed_checks is not None:
            save_failed_checks(self, failed_checks)

        # We parametrize update of stats to make testing easier.
        if update_stats:
            # Update stats AFTER changing approval status.
            stats_after = self.entity.get_stats(self.locale)
            stats_diff = Entity.get_stats_diff(stats_before, stats_after)
            translatedresource.adjust_all_stats(**stats_diff)

    def update_latest_translation(self):
        """
        Set `latest_translation` to this translation if its more recent than
        the currently stored translation. Do this for all affected models.
        """
        resource = self.entity.resource
        project = resource.project
        locale = self.locale

        to_update = [
            (TranslatedResource, Q(Q(resource=resource) & Q(locale=locale))),
            (ProjectLocale, Q(Q(project=project) & Q(locale=locale))),
            (Project, Q(pk=project.pk)),
        ]

        if not project.system_project:
            to_update.append((Locale, Q(pk=locale.pk)))

        for model, query in to_update:
            model.objects.filter(
                Q(
                    query
                    & Q(
                        Q(latest_translation=None)
                        | Q(latest_translation__date__lt=self.latest_activity["date"])
                    )
                )
            ).update(latest_translation=self)

    def approve(self, user):
        """
        Approve translation.
        """
        self.approved = True
        self.approved_user = user
        self.approved_date = timezone.now()

        self.pretranslated = False
        self.fuzzy = False

        self.unapproved_user = None
        self.unapproved_date = None

        self.rejected = False
        self.rejected_user = None
        self.rejected_date = None

        self.save()

        if not self.memory_entries.exists():
            TranslationMemoryEntry.objects.create(
                source=self.tm_source,
                target=self.tm_target,
                entity=self.entity,
                translation=self,
                locale=self.locale,
                project=self.entity.resource.project,
            )

        self.mark_changed()

    def unapprove(self, user):
        """
        Unapprove translation.
        """
        self.approved = False
        self.unapproved_user = user
        self.unapproved_date = timezone.now()
        self.save()

        TranslationMemoryEntry.objects.filter(translation=self).delete()
        self.mark_changed()

    def reject(self, user):
        """
        Reject translation.
        """
        # Check if translation was approved or pretranslated or fuzzy.
        # We must do this before rejecting it.
        if self.approved or self.pretranslated or self.fuzzy:
            TranslationMemoryEntry.objects.filter(translation=self).delete()
            self.mark_changed()

        self.rejected = True
        self.rejected_user = user
        self.rejected_date = timezone.now()
        self.approved = False
        self.approved_user = None
        self.approved_date = None
        self.pretranslated = False
        self.fuzzy = False
        self.save()

    def unreject(self, user):
        """
        Unreject translation.
        """
        self.rejected = False
        self.unrejected_user = user
        self.unrejected_date = timezone.now()
        self.save()

    def serialize(self):
        return {
            "pk": self.pk,
            "string": self.string,
            "approved": self.approved,
            "rejected": self.rejected,
            "pretranslated": self.pretranslated,
            "fuzzy": self.fuzzy,
            "errors": [error.message for error in self.errors.all()],
            "warnings": [warning.message for warning in self.warnings.all()],
        }

    def mark_changed(self):
        """
        Mark the given locale as having changed translations since the
        last sync.
        """
        if self.entity.resource.project.data_source == Project.DataSource.DATABASE:
            return

        ChangedEntityLocale.objects.get_or_create(
            entity=self.entity, locale=self.locale
        )


class TranslationMemoryEntryQuerySet(models.QuerySet):
    def postgres_levenshtein_ratio(
        self, text, min_quality, min_dist, max_dist, levenshtein_param=None
    ):
        """
        Filter TranslationMemory entries fully in PostgreSQL.
        `levenshtein` function is provided by `fuzzystrmatch` module.
        All strings are initially pre-filtered with min_dist and max_dist.

        :arg str text: reference string to search in Translation Memory
        :arg float min_quality: minimal quality of a levenshtein ratio
        :arg int min_dist: minimum length distance from a text string
        :arg int max_dist: maximum length distance from a text string
        :arg django.db.models.Func levenshtein_param: a field or a sql expression, the first
            argument of the levenshtein distance function. Default: the 'source' column.
        :return: TranslationMemory Entries enriched with the quality metric.
        """
        text_length = Value(len(text))

        source_target_length = Length(F("source")) + text_length

        levenshtein_param = levenshtein_param or F("source")
        levenshtein_distance_expression = LevenshteinDistance(
            levenshtein_param,
            Value(text),
            1,
            2,
            2,
        )

        entries = self.annotate(
            source_length=Length(F("source")),
            quality=ExpressionWrapper(
                (
                    Cast(
                        (source_target_length - levenshtein_distance_expression),
                        models.FloatField(),
                    )
                    / source_target_length
                )
                * 100,
                output_field=models.DecimalField(),
            ),
        ).filter(
            source_length__gte=min_dist,
            source_length__lte=max_dist,
            quality__gt=min_quality * 100,
        )
        return entries

    def python_levenshtein_ratio(self, text, min_quality, min_dist, max_dist):
        """
        Filter TranslationMemory entries in Python, with the initial pre-filtering of
        entities in the PostgreSQL.  All strings are initially pre-filtered
        with min_dist and max_dist.

        All implementations of the Levenshtein ratio algorithm have to return a QuerySet with
        annotated with the quality column.

        In the case of the in-memory (python) version, this method will make 2 queries
        to the database:
        1. initial set of pre-filtered possible matches
        2. a queryset with matches annotated with the quality column

        Extra query is made because there's no easy way to create a QuerySet
        from already fetched data and it's not possible to annotate it with additional columns.

        :arg str text: reference string to search in  TM
        :arg float min_quality: minimal quality of a levenshtein ratio
        :arg int min_dist: minimum length distance from a text string
        :arg int max_dist: maximum length distance from a text string
        :return: TranslationMemory Entries enriched with the quality metric.
        """
        # To minimalize number of entries to scan in Python. pre-filter TM entries
        # with a substring of the original string limited to 255 characters.

        possible_matches = self.postgres_levenshtein_ratio(
            text[:255],
            min_quality,
            min_dist,
            max_dist,
            Substr(F("source"), 1, 255),
        ).values_list("pk", "source")

        matches_pks = []

        # In order to keep compatibility with `postgresql_levenshtein_ratio`,
        # entries are annotate with the quality column.
        quality_sql_map = []

        for pk, source in possible_matches:
            quality = Levenshtein.ratio(text, source)

            if quality > min_quality:
                matches_pks.append(pk)
                quality_sql_map.append(When(pk=pk, then=Value(quality * 100)))

        entries = self.filter(pk__in=matches_pks,).annotate(
            quality=Case(
                *quality_sql_map,
                **dict(
                    default=Value(0),
                    output_field=models.DecimalField(),
                ),
            )
        )
        return entries

    def minimum_levenshtein_ratio(self, text, min_quality=0.7):
        """
        Returns entries that match minimal levenshtein_ratio
        """
        # Only check entities with similar length
        length = len(text)
        min_dist = int(math.ceil(max(length * min_quality, 2)))
        max_dist = int(math.floor(min(length / min_quality, 1000)))

        get_matches = self.postgres_levenshtein_ratio

        if min_dist > 255 or max_dist > 255:
            get_matches = self.python_levenshtein_ratio

        return get_matches(
            text,
            min_quality,
            min_dist,
            max_dist,
        )


class TranslationMemoryEntry(models.Model):
    source = models.TextField()
    target = models.TextField()

    entity = models.ForeignKey(
        Entity, models.SET_NULL, null=True, related_name="memory_entries"
    )
    translation = models.ForeignKey(
        Translation, models.SET_NULL, null=True, related_name="memory_entries"
    )
    locale = models.ForeignKey(Locale, models.CASCADE)
    project = models.ForeignKey(
        Project, models.SET_NULL, null=True, related_name="memory_entries"
    )

    objects = TranslationMemoryEntryQuerySet.as_manager()


class TranslatedResourceQuerySet(models.QuerySet):
    def aggregated_stats(self):
        return self.aggregate(
            total=Sum("resource__total_strings"),
            approved=Sum("approved_strings"),
            pretranslated=Sum("pretranslated_strings"),
            errors=Sum("strings_with_errors"),
            warnings=Sum("strings_with_warnings"),
            unreviewed=Sum("unreviewed_strings"),
        )

    def aggregate_stats(self, instance):
        aggregated_stats = self.aggregated_stats()

        instance.total_strings = aggregated_stats["total"] or 0
        instance.approved_strings = aggregated_stats["approved"] or 0
        instance.pretranslated_strings = aggregated_stats["pretranslated"] or 0
        instance.strings_with_errors = aggregated_stats["errors"] or 0
        instance.strings_with_warnings = aggregated_stats["warnings"] or 0
        instance.unreviewed_strings = aggregated_stats["unreviewed"] or 0

        instance.save(
            update_fields=[
                "total_strings",
                "approved_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
            ]
        )

    def stats(self, project, paths, locale):
        """
        Returns statistics for the given project, paths and locale.
        """
        translated_resources = self.filter(
            locale=locale,
            resource__project__disabled=False,
        )

        if project.slug == "all-projects":
            translated_resources = translated_resources.filter(
                resource__project__system_project=False,
                resource__project__visibility=Project.Visibility.PUBLIC,
            )
        else:
            translated_resources = translated_resources.filter(
                resource__project=project,
            )

            if paths:
                translated_resources = translated_resources.filter(
                    resource__path__in=paths,
                )

        return translated_resources.aggregated_stats()

    def update_stats(self):
        """
        Update stats on a list of TranslatedResource.
        """
        self = self.prefetch_related("resource__project", "locale")

        locales = Locale.objects.filter(
            translatedresources__in=self,
        ).distinct()

        projects = Project.objects.filter(
            resources__translatedresources__in=self,
        ).distinct()

        projectlocales = ProjectLocale.objects.filter(
            project__resources__translatedresources__in=self,
            locale__translatedresources__in=self,
        ).distinct()

        for translated_resource in self:
            translated_resource.calculate_stats(save=False)

        TranslatedResource.objects.bulk_update(
            list(self),
            fields=[
                "total_strings",
                "approved_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
            ],
        )

        for project in projects:
            project.aggregate_stats()

        for locale in locales:
            locale.aggregate_stats()

        for projectlocale in projectlocales:
            projectlocale.aggregate_stats()


class TranslatedResource(AggregatedStats):
    """
    Resource representation for a specific locale.
    """

    resource = models.ForeignKey(
        Resource, models.CASCADE, related_name="translatedresources"
    )
    locale = models.ForeignKey(
        Locale, models.CASCADE, related_name="translatedresources"
    )

    #: Most recent translation approved or created for this translated
    #: resource.
    latest_translation = models.ForeignKey(
        "Translation",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="resource_latest",
    )

    objects = TranslatedResourceQuerySet.as_manager()

    class Meta:
        unique_together = (("locale", "resource"),)

    def adjust_all_stats(self, *args, **kwargs):
        project = self.resource.project
        locale = self.locale

        project_locale = utils.get_object_or_none(
            ProjectLocale,
            project=project,
            locale=locale,
        )

        self.adjust_stats(*args, **kwargs)
        project.adjust_stats(*args, **kwargs)

        if not project.system_project:
            locale.adjust_stats(*args, **kwargs)

        if project_locale:
            project_locale.adjust_stats(*args, **kwargs)

    def calculate_stats(self, save=True):
        """Update stats, including denormalized ones."""
        resource = self.resource
        locale = self.locale

        entity_ids = Translation.objects.filter(locale=locale).values("entity")
        translated_entities = Entity.objects.filter(
            pk__in=entity_ids, resource=resource, obsolete=False
        )

        # Singular
        translations = Translation.objects.filter(
            entity__in=translated_entities.filter(string_plural=""),
            locale=locale,
        )

        approved = translations.filter(
            approved=True,
            errors__isnull=True,
            warnings__isnull=True,
        ).count()

        pretranslated = translations.filter(
            pretranslated=True,
            errors__isnull=True,
            warnings__isnull=True,
        ).count()

        errors = (
            translations.filter(
                Q(
                    Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                    & Q(errors__isnull=False)
                ),
            )
            .distinct()
            .count()
        )

        warnings = (
            translations.filter(
                Q(
                    Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                    & Q(warnings__isnull=False)
                ),
            )
            .distinct()
            .count()
        )

        unreviewed = translations.filter(
            approved=False,
            rejected=False,
            pretranslated=False,
            fuzzy=False,
        ).count()

        # Plural
        nplurals = locale.nplurals or 1
        for e in translated_entities.exclude(string_plural="").values_list("pk"):
            translations = Translation.objects.filter(
                entity_id=e,
                locale=locale,
            )

            plural_approved_count = translations.filter(
                approved=True,
                errors__isnull=True,
                warnings__isnull=True,
            ).count()

            plural_pretranslated_count = translations.filter(
                pretranslated=True,
                errors__isnull=True,
                warnings__isnull=True,
            ).count()

            if plural_approved_count == nplurals:
                approved += 1
            elif plural_pretranslated_count == nplurals:
                pretranslated += 1
            else:
                plural_errors_count = (
                    translations.filter(
                        Q(
                            Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                            & Q(errors__isnull=False)
                        ),
                    )
                    .distinct()
                    .count()
                )

                plural_warnings_count = (
                    translations.filter(
                        Q(
                            Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                            & Q(warnings__isnull=False)
                        ),
                    )
                    .distinct()
                    .count()
                )

                if plural_errors_count:
                    errors += 1
                elif plural_warnings_count:
                    warnings += 1

            plural_unreviewed_count = translations.filter(
                approved=False, pretranslated=False, fuzzy=False, rejected=False
            ).count()
            if plural_unreviewed_count:
                unreviewed += plural_unreviewed_count

        if not save:
            self.total_strings = resource.total_strings
            self.approved_strings = approved
            self.pretranslated_strings = pretranslated
            self.strings_with_errors = errors
            self.strings_with_warnings = warnings
            self.unreviewed_strings = unreviewed

            return False

        # Calculate diffs to reduce DB queries
        total_strings_diff = resource.total_strings - self.total_strings
        approved_strings_diff = approved - self.approved_strings
        pretranslated_strings_diff = pretranslated - self.pretranslated_strings
        strings_with_errors_diff = errors - self.strings_with_errors
        strings_with_warnings_diff = warnings - self.strings_with_warnings
        unreviewed_strings_diff = unreviewed - self.unreviewed_strings

        self.adjust_all_stats(
            total_strings_diff,
            approved_strings_diff,
            pretranslated_strings_diff,
            strings_with_errors_diff,
            strings_with_warnings_diff,
            unreviewed_strings_diff,
        )
