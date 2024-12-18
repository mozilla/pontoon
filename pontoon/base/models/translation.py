from dirtyfields import DirtyFieldsMixin

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.actionlog.utils import log_action
from pontoon.base import utils
from pontoon.base.fluent import get_simple_preview
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.base.models.entity import Entity
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.base.models.user import User
from pontoon.checks import DB_FORMATS
from pontoon.checks.utils import save_failed_checks


class TranslationQuerySet(models.QuerySet):
    def translated_resources(self, locale):
        from pontoon.base.models.translated_resource import TranslatedResource

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
        GPT_TRANSFORM = "gpt-transform", "GPT Transform"

    machinery_sources = ArrayField(
        models.CharField(max_length=30, choices=MachinerySource.choices),
        default=list,
        blank=True,
    )

    objects = TranslationQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["entity", "user", "approved", "pretranslated"]),
            models.Index(fields=["entity", "locale", "approved"]),
            models.Index(fields=["entity", "locale", "pretranslated"]),
            models.Index(fields=["entity", "locale", "fuzzy"]),
            models.Index(fields=["locale", "user", "entity"]),
            models.Index(fields=["date", "locale"]),
            models.Index(fields=["approved_date", "locale"]),
        ]
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

    def save(self, failed_checks=None, *args, **kwargs):
        from pontoon.base.models.translated_resource import TranslatedResource
        from pontoon.base.models.translation_memory import TranslationMemoryEntry

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
                    is_implicit_action=True,
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
        translatedresource, created = TranslatedResource.objects.get_or_create(
            resource=self.entity.resource, locale=self.locale
        )

        # Update latest translation where necessary
        self.update_latest_translation()

        # Failed checks must be saved before stats are updated (bug 1521606)
        if failed_checks is not None:
            save_failed_checks(self, failed_checks)

        # Update stats AFTER changing approval status.
        stats_after = self.entity.get_stats(self.locale)
        stats_diff = {
            stat_name: stats_after[stat_name] - stats_before[stat_name]
            for stat_name in stats_before
        }
        if created:
            stats_diff["total_strings_diff"] = translatedresource.count_total_strings()
        translatedresource.adjust_all_stats(**stats_diff)

    def update_latest_translation(self):
        """
        Set `latest_translation` to this translation if its more recent than
        the currently stored translation. Do this for all affected models.
        """
        from pontoon.base.models.translated_resource import TranslatedResource

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
        from pontoon.base.models.translation_memory import TranslationMemoryEntry

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
        from pontoon.base.models.translation_memory import TranslationMemoryEntry

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
        from pontoon.base.models.translation_memory import TranslationMemoryEntry

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
            "errors": (
                [error.message for error in self.errors.all()] if self.pk else []
            ),
            "warnings": (
                [warning.message for warning in self.warnings.all()] if self.pk else []
            ),
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
