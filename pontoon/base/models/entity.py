from collections.abc import Iterable

from dirtyfields import DirtyFieldsMixin

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Prefetch
from django.utils import timezone

from pontoon.base.models.locale import Locale
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.base.models.section import Section


class EntityQuerySet(models.QuerySet["Entity"]):
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
    resource: models.ForeignKey["Resource"] = models.ForeignKey(
        Resource, models.CASCADE, related_name="entities"
    )
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
