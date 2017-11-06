from __future__ import unicode_literals

from collections import defaultdict
import logging

from bulk_update.helper import bulk_update
from django.db import models
from django.db import transaction

from pontoon.base.models import (
    Entity,
    Locale,
)

from pontoon.base.utils import (
    get_words,
    get_singulars
)
from pontoon.terminology.term_indexes import DBTermIndex

log = logging.getLogger(__name__)


class TermManager(models.Manager):
    term_index = DBTermIndex

    def find_terms(self, original_string, entity_singulars):
        """Return terms ids and associated phrases in string."""
        terms_phrases = defaultdict(set)
        original_string_words = get_words(original_string, lower=False)
        entity_singular_words = entity_singulars.split()

        # Search for terms that could be good candidates to match them with the entity string.
        candidates = self.term_index.get_terms_candidates(entity_singulars)

        # Algorithm for matching
        # 1. Sort candidates by length in descending order to match the longest terms first
        # 2. Scan list of words to check if term exists inside the string
        # 3. If it exists, add it to the dict of terms with matched phrase and remove
        # a phrase from string to to avoid duplicates from terms with the same
        # word prefix (e.g. mail and mail client).
        # 4. If not, scan again. If scan throws valueError, jump to the next term.
        sorted_terms = sorted(
            candidates.items(),
            key=lambda t: (len(t[0].split()), t[0]),
            reverse=True
        )
        for term_singulars, term_pks in sorted_terms:
            scan_start = 0
            term_words = term_singulars.split()
            term_len = len(term_words)

            while True:
                try:
                    scan_start += (entity_singular_words[scan_start:]).index(term_words[0])
                    scan_end = scan_start + term_len
                    if entity_singular_words[scan_start:scan_end] == term_words:
                        phrase = ' '.join(
                            original_string_words[scan_start:scan_end]
                        )
                        terms_phrases[phrase].update(term_pks)
                        del entity_singular_words[scan_start:scan_end]
                        del original_string_words[scan_start:scan_end]
                    else:
                        scan_start = scan_end
                except ValueError:
                    break

        return terms_phrases.items()

    @transaction.atomic
    def assign_terms_to_entities(self, entities):
        entity_terms = []
        entities_pks = [e[0] for e in entities]
        # Remove existing terms relations.
        EntityTerm.objects.filter(entity__in=entities_pks).delete()
        for entity_pk, string, string_singulars, string_plural, string_plural_singulars in entities:
            if string_singulars:
                entity_terms.extend([
                    (entity_pk, term_pks, phrase)
                    for (phrase, term_pks) in self.find_terms(string, string_singulars)
                ])

            if string_plural_singulars:
                entity_terms.extend([
                    (entity_pk, term_pks, phrase)
                    for (phrase, term_pks) in self.find_terms(
                        string_plural, string_plural_singulars)
                ])
        terms_db = []

        for entity_pk, terms, phrase in entity_terms:
            for term_pk in terms:
                terms_db.append(
                    EntityTerm(entity_id=entity_pk, term_id=term_pk, phrase=phrase)
                )
        EntityTerm.objects.bulk_create(terms_db, 10000)

        terms_count = (
            Term.objects.filter(entityterm__entity__pk__in=entities_pks)
            .distinct()
            .count()
        )

        phrases_count = (
            EntityTerm.objects.filter(entity__pk__in=entities_pks)
            .distinct()
            .count()
        )

        log.info(
            'Assigned %s terms to %s entities and matched %s phrases.',
            terms_count,
            len(entities),
            phrases_count
        )

    @transaction.atomic
    def import_tbx_terms(self, tbx_terms):
        """
        Creates/updates term objects passed from terminology files.
        All terms will be automatically matched with their entities.

        :param VCSTerm tbx_terms: a list of terms imported from the filesystem/vcs.
        """
        db_terms = {}

        for term in Term.objects.all():
            db_terms[term.term_id] = term

        new_terms = []
        update_terms = []
        updated_records = 0

        for term_id, term in tbx_terms.items():
            try:
                db_term = db_terms[term.term_id]
                db_term.part_of_speech = term.part_of_speech
                db_term.description = term.description
                update_terms.append(db_term)
                updated_records += 1
            except KeyError:
                new_terms.append(
                    Term(
                        term_id=term.term_id,
                        source_term=term.source_text,
                        source_term_singulars=' '.join(get_singulars(term.source_text)),
                        note=term.part_of_speech or '',
                        description=term.description or '',
                    )
                )

        if update_terms:
            bulk_update(update_terms, update_fields=['note', 'description'], batch_size=100)
            log.info('Updated {} existing terms.'.format(updated_records))

        if new_terms:
            self.bulk_create(new_terms, 1000)
            log.info('Inserted {} new terms.'.format(len(new_terms)))

        changed_terms = (new_terms + update_terms)

        locale_cache = {locale.code: locale for locale in Locale.objects.all()}
        update_translations = []
        for term in changed_terms:
            vcs_term = tbx_terms[term.term_id]
            for locale_code, translations in vcs_term.translations.items():
                for translation in translations:
                    update_translations.append(
                        TermTranslation(
                            locale=locale_cache[locale_code],
                            text=translation,
                            term=term,
                        )
                    )
        TermTranslation.objects.bulk_create(update_translations)

        log.info('Updated {} translations of terms.'.format(len(update_translations)))
        self.assign_terms_to_entities(
            Entity.objects.values_list(
                'pk',
                'string',
                'string_singulars',
                'string_plural',
                'string_plural_singulars'
            )
        )


class EntityTerm(models.Model):
    """
    Binds terminology term to a specific part of a string from an entity.
    """
    """Part of entity string which should be highlighted."""
    phrase = models.TextField()
    entity = models.ForeignKey(Entity, related_name='terms')
    term = models.ForeignKey('Term', on_delete=models.CASCADE)


class Term(models.Model):
    """
    Defines a single term entry.
    """

    """Unique identified of term imported from the tbx file."""
    term_id = models.CharField(max_length=30, unique=True)

    """Source string (in en-US) that contains value to search in strings."""
    source_term = models.TextField(db_index=True)

    """
    Stems from source_text, we store them to avoid expensive stemming operations
    during metching terminology terms with entities.
    """
    source_term_singulars = models.TextField(db_index=True)

    """Contains the part of speech."""
    note = models.TextField(blank=True)

    """Description of term, adds more context."""
    description = models.TextField(blank=True)

    objects = TermManager()

    def __unicode__(self):
        return self.source_term

    def serialize(self, locale=None):
        if locale:
            translations = self.translations.filter(locale=locale)
        else:
            translations = self.translations.all()

        term = {
            u'note': self.note,
            u'term': self.source_term,
            u'description': self.description,
            u'translations': [t.text for t in translations]
        }

        return term


class TermTranslation(models.Model):
    """
    Map of translations, locales codes are keys and translations are values.
    """
    locale = models.ForeignKey(Locale, related_name='terms_translations')
    term = models.ForeignKey(Term, related_name='translations')

    text = models.TextField()
