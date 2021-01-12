import re

from django.db import models

from pontoon.base.models import Entity, ProjectLocale, Resource, TranslatedResource


def update_terminology_project_stats():
    resource = Resource.objects.get(project__slug="terminology")
    project = resource.project
    total_strings = Entity.objects.filter(resource=resource, obsolete=False).count()
    resource.total_strings = total_strings
    resource.save(update_fields=["total_strings"])

    translated_resources = list(TranslatedResource.objects.filter(resource=resource))

    for translated_resource in translated_resources:
        translated_resource.calculate_stats(save=False)

    TranslatedResource.objects.bulk_update(
        translated_resources,
        [
            "total_strings",
            "approved_strings",
            "fuzzy_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
        ],
    )

    project.aggregate_stats()

    for locale in project.locales.all():
        locale.aggregate_stats()

    for projectlocale in ProjectLocale.objects.filter(project=project):
        projectlocale.aggregate_stats()


class TermQuerySet(models.QuerySet):
    def for_string(self, string):
        terms = []
        available_terms = self.exclude(definition="").exclude(forbidden=True)

        for term in available_terms:
            term_text = r"\b" + re.escape(term.text)
            flags = 0 if term.case_sensitive else re.IGNORECASE

            if re.search(term_text, string, flags):
                terms.append(term)

        return terms


class Term(models.Model):
    text = models.CharField(max_length=255)
    entity = models.OneToOneField("base.Entity", models.SET_NULL, null=True, blank=True)

    class PartOfSpeech(models.TextChoices):
        ADJECTIVE = "adjective", "Adjective"
        ADVERB = "adverb", "Adverb"
        NOUN = "noun", "Noun"
        VERB = "verb", "Verb"

    part_of_speech = models.CharField(max_length=50, choices=PartOfSpeech.choices)

    definition = models.TextField(blank=True)
    usage = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Status(models.TextChoices):
        APPROVED = "approved", "Approved"
        NEW = "new", "New"
        OBSOLETE = "obsolete", "Obsolete"
        REVIEW = "review", "Review"

    status = models.CharField(
        max_length=20, choices=Status.choices, null=True, blank=True
    )

    case_sensitive = models.BooleanField(default=False)
    exact_match = models.BooleanField(default=False)
    do_not_translate = models.BooleanField(default=False)
    forbidden = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "auth.User", models.SET_NULL, related_name="terms", null=True, blank=True
    )

    objects = TermQuerySet.as_manager()

    def translation(self, locale):
        """
        Get locale translation of the term.
        """
        if self.do_not_translate:
            return self.text
        else:
            try:
                return self.translations.get(locale=locale).text
            except (AttributeError, TermTranslation.DoesNotExist):
                return None

    @property
    def localizable(self):
        """
        Check if the term is localizable.
        """
        if self.do_not_translate:
            return False

        if self.forbidden:
            return False

        if self.definition == "":
            return False

        return True

    def entity_comment(self):
        """
        Generate entity comment from the term.
        """
        comment = "{}. {}.".format(
            self.part_of_speech.capitalize(), self.definition.capitalize().rstrip("."),
        )

        if self.usage:
            comment += " E.g. {}.".format(self.usage.capitalize().rstrip("."))

        return comment

    def create_entity(self):
        """
        An Entity must be created (or deobsoleted) for a Term according to the
        following rules:
        - Entity.string contains content of Term.text.
        - Entity.comment contains joint content of several fields:
          Term.part_of_speech. Term.definition. E.g.: Term.usage.
        """
        resource = Resource.objects.get(project__slug="terminology")

        entity, created = Entity.objects.get_or_create(
            string=self.text, comment=self.entity_comment(), resource=resource,
        )

        # Using update() to avoid circular Term.save() call
        Term.objects.filter(pk=self.pk).update(entity_id=entity.id)

        if not created:
            entity.obsolete = False
            entity.save(update_fields=["obsolete"])

        # Make sure Term entities are ordered alphabetically
        entities = list(
            Entity.objects.filter(resource=resource, obsolete=False).order_by("string")
        )
        for index, e in enumerate(entities):
            e.order = index
        Entity.objects.bulk_update(entities, ["order"])

    def obsolete_entity(self):
        entity = self.entity

        # Ignore if term doesn't have entity assigned
        if entity is None:
            return

        entity.obsolete = True
        entity.save(update_fields=["obsolete"])

    def handle_term_update(self):
        """
        Before updating an existing Term, update its Entity if neccessary
        """
        term = self
        old_term = Term.objects.get(pk=term.pk)

        # Ignore changes to non-localizable terms that stay non-localizable
        if not old_term.localizable and not term.localizable:
            return

        # If localizable term becomes non-localizable, obsolete its Entity
        if old_term.localizable and not term.localizable:
            old_term.obsolete_entity()

        # If non-localizable term becomes localizable, create a corresponding Entity
        elif not old_term.localizable and term.localizable:
            term.create_entity()

        # If relevant changes are made to the localizable term that stays localizable
        else:
            # If Term.text changes, a new Entity instance gets created and the previous one becomes obsolete.
            if old_term.text != term.text:
                old_term.obsolete_entity()
                term.create_entity()

            # If Term.part_of_speech, Term.definition or Term.usage change, Entity.comment gets updated.
            elif (
                old_term.part_of_speech != term.part_of_speech
                or old_term.definition != term.definition
                or old_term.usage != term.usage
            ):
                entity = term.entity

                # Ignore if term doesn't have entity assigned
                if entity is None:
                    return

                entity.comment = term.entity_comment()
                entity.save(update_fields=["comment"])

                return

        update_terminology_project_stats()

    def handle_term_create(self):
        """
        After creating a new localizable Term, create its Entity
        """
        self.create_entity()
        update_terminology_project_stats()

    def save(self, *args, **kwargs):
        created = self.pk is None

        if not created:
            self.handle_term_update()

        super(Term, self).save(*args, **kwargs)

        if created and self.localizable:
            self.handle_term_create()

    def delete(self, *args, **kwargs):
        """
        Before deleting a Term, obsolete its Entity
        """
        self.obsolete_entity()
        update_terminology_project_stats()

        super(Term, self).delete(*args, **kwargs)

    def __str__(self):
        return self.text


class TermTranslation(models.Model):
    term = models.ForeignKey(Term, models.CASCADE, related_name="translations")
    locale = models.ForeignKey("base.Locale", models.CASCADE, related_name="terms")

    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
