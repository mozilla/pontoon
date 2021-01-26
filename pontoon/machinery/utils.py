import json
import logging
import operator
from collections import defaultdict
from functools import reduce

import Levenshtein
import requests
from django.conf import settings
from django.db.models import F, Q

import pontoon.base as base

log = logging.getLogger(__name__)
MAX_RESULTS = 5


def get_google_translate_data(text, locale_code):
    api_key = settings.GOOGLE_TRANSLATE_API_KEY

    if not api_key:
        log.error("GOOGLE_TRANSLATE_API_KEY not set")
        return {
            "status": False,
            "message": "Bad Request: Missing api key.",
        }

    url = "https://translation.googleapis.com/language/translate/v2"

    payload = {
        "q": text,
        "source": "en",
        "target": locale_code,
        "format": "text",
        "key": api_key,
    }

    try:
        r = requests.post(url, params=payload)
        r.raise_for_status()
        root = json.loads(r.content)

        if "data" not in root:
            log.error("Google Translate error: {error}".format(error=root))
            return {
                "status": False,
                "message": "Bad Request: {error}".format(error=root),
            }

        return {
            "status": True,
            "translation": root["data"]["translations"][0]["translatedText"],
        }

    except requests.exceptions.RequestException as e:
        log.error("Google Translate error: {error}".format(error=e))
        return {
            "status": False,
            "message": "{error}".format(error=e),
        }


def get_concordance_search_data(text, locale):
    search_phrases = base.utils.get_search_phrases(text)
    search_filters = (
        Q(
            Q(target__icontains_collate=(phrase, locale.db_collation))
            | Q(source__icontains=phrase),
            locale=locale,
        )
        for phrase in search_phrases
    )
    search_query = reduce(operator.and_, search_filters)

    search_results = (
        base.models.TranslationMemoryEntry.objects.filter(search_query)
        .annotate(
            entity_pk=F("entity__pk"),
            project_name=F("project__name"),
            project_slug=F("project__slug"),
        )
        .values("source", "target", "entity_pk", "project_name", "project_slug")
        .distinct()
    )

    def sort_by_quality(entity):
        """Sort the results by their best Levenshtein distance from the search query"""
        return (
            max(
                int(round(Levenshtein.ratio(text, entity["target"]) * 100)),
                int(round(Levenshtein.ratio(text, entity["source"]) * 100)),
            ),
            entity["target"],
        )

    return sorted(search_results, key=sort_by_quality, reverse=True)


def get_translation_memory_data(text, locale, pk=None):
    entries = (
        base.models.TranslationMemoryEntry.objects.filter(locale=locale)
        .minimum_levenshtein_ratio(text)
        .exclude(translation__approved=False, translation__fuzzy=False)
    )

    # Exclude existing entity
    if pk:
        entries = entries.exclude(entity__pk=pk)

    entries = entries.values("source", "target", "quality")
    entries_merged = defaultdict(lambda: {"count": 0, "quality": 0})

    # Group entries with the same target and count them
    for entry in entries:
        if (
            entry["target"] not in entries_merged
            or entry["quality"] > entries_merged[entry["target"]]["quality"]
        ):
            entries_merged[entry["target"]].update(entry)
        entries_merged[entry["target"]]["count"] += 1

    return sorted(
        entries_merged.values(), key=lambda e: (e["quality"], e["count"]), reverse=True,
    )[:MAX_RESULTS]
