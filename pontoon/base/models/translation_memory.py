from math import ceil, floor

import Levenshtein

from django.db import models
from django.db.models import Case, ExpressionWrapper, F, Value, When
from django.db.models.functions import Cast, Length, Substr

from pontoon.base.models.entity import Entity
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.translation import Translation
from pontoon.db import LevenshteinDistance


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

        entries = self.filter(
            pk__in=matches_pks,
        ).annotate(
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
        min_dist = int(ceil(max(length * min_quality, 2)))
        max_dist = int(floor(min(length / min_quality, 1000)))

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
