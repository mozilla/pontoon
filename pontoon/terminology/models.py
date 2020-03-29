import re

from sacremoses import MosesTokenizer

from django.db import models


class TermQuerySet(models.QuerySet):
    def for_string(self, string):
        term_pks = []
        valid_terms = self.exclude(definition="").exclude(forbidden=True)
        mt = MosesTokenizer()
        source_words = mt.tokenize(string)

        for term in valid_terms:
            flags = 0 if term.case_sensitive else re.IGNORECASE
            terms_words = mt.tokenize(term.text)

            if len(terms_words) == 1:
                for word in source_words:
                    if re.search(terms_words[0], word, flags):
                        term_pks.append(term.pk)
                        break
            else:
                if re.search("".join(terms_words), "".join(source_words), flags):
                    term_pks.append(term.pk)

        return self.filter(pk__in=term_pks)


class Term(models.Model):
    text = models.CharField(max_length=255)

    PARTS_OF_SPEECH = (
        ("adjective", "Adjective"),
        ("adverb", "Adverb"),
        ("noun", "Noun"),
        ("verb", "Verb"),
    )
    part_of_speech = models.CharField(max_length=50, choices=PARTS_OF_SPEECH)

    definition = models.TextField(blank=True)
    usage = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    STATUSES = (
        ("approved", "Approved"),
        ("new", "New"),
        ("obsolete", "Obsolete"),
        ("review", "Review"),
    )
    status = models.CharField(max_length=20, choices=STATUSES, null=True, blank=True)

    case_sensitive = models.BooleanField(default=False)
    exact_match = models.BooleanField(default=False)
    do_not_translate = models.BooleanField(default=False)
    forbidden = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "auth.User", models.CASCADE, related_name="terms", null=True, blank=True
    )

    objects = TermQuerySet.as_manager()

    def translation(self, locale):
        if self.do_not_translate:
            return self.text
        else:
            try:
                return self.translations.filter(locale=locale).first().text
            except AttributeError:
                return None

    def __str__(self):
        return self.text


class TermTranslation(models.Model):
    term = models.ForeignKey(Term, models.CASCADE, related_name="translations")
    locale = models.ForeignKey("base.Locale", models.CASCADE, related_name="terms")

    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
