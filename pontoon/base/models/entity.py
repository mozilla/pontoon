from typing import TYPE_CHECKING, Any

from dirtyfields import DirtyFieldsMixin  # type: ignore[import-untyped]

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from pontoon.base.models.locale import Locale
from pontoon.base.models.resource import Resource
from pontoon.base.models.section import Section


if TYPE_CHECKING:
    from pontoon.base.models.comment import Comment
    from pontoon.base.models.translation import TranslationQuerySet
    from pontoon.terminology.models import Term


class Entity(DirtyFieldsMixin, models.Model):
    resource: models.ForeignKey["Resource"] = models.ForeignKey(
        Resource, models.CASCADE, related_name="entities"
    )
    section: models.ForeignKey[Section | None] = models.ForeignKey(
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

    changed_locales: "models.ManyToManyField[Locale, Any]" = models.ManyToManyField(
        Locale,
        through="ChangedEntityLocale",
        help_text="List of locales in which translations for this entity have "
        "changed since the last sync.",
    )

    comments: models.QuerySet["Comment"]
    """Actually a RelatedManager"""
    term: "Term"
    translation_set: "TranslationQuerySet"
    """Actually a RelatedManager"""

    class Meta:
        indexes = [models.Index(fields=["resource", "obsolete"])]

    def __str__(self):
        return self.string

    def has_changed(self, locale: Locale) -> bool:
        """
        Check if translations in the given locale have changed since the
        last sync.
        """
        return locale in self.changed_locales.all()

    def reset_active_translation(self, locale: Locale) -> dict[str, Any] | None:
        """
        Reset active translation for given entity and locale.

        Return data for the active translation if it exists, or None otherwise.
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

            return active_translation.serialize()
        else:
            return None

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
