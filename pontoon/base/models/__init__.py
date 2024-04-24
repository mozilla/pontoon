import math

import Levenshtein

from dirtyfields import DirtyFieldsMixin
from django.db.models.functions import Length, Substr, Cast
from django.contrib.postgres.fields import ArrayField

from django.db import models
from django.db.models import (
    Count,
    F,
    Q,
    Sum,
    Case,
    When,
    Value,
    ExpressionWrapper,
)
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.actionlog.utils import log_action
from pontoon.base import utils
from pontoon.base.fluent import get_simple_preview
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.base.models.comment import Comment
from pontoon.base.models.aggregated_stats import AggregatedStats
from pontoon.base.models.entity import Entity, get_word_count
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
