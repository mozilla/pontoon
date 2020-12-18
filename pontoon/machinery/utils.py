import json
import logging
import operator
import requests

from collections import defaultdict
from functools import reduce

from django.conf import settings
from django.db.models import Value, Q, F

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
            "message": "Bad Request: {error}".format(error=e),
        }


def get_concordance_search_results(text, locale, pk=None):
    search_list = base.utils.get_search_phrases(text)
    search_query_list = [(s, locale.db_collation) for s in search_list]
    search_filters = (
        Q(target__icontains_collate=(phrase, collation)) | Q(source__icontains=phrase)
        for phrase, collation in search_query_list
    )
    search_filters = (
        Q(target__icontains_collate=(phrase, collation)) | Q(source__icontains=phrase)
        for phrase, collation in search_query_list
    )
    search_query = reduce(operator.and_, search_filters)

    results = base.models.TranslationMemoryEntry.objects.filter(
        search_query  # , locale=locale
    ).search_result_quality(
        # Calculate the quality of the results based on the Levenhstein's distance
        " ".join(search_list),
        F("target"),
    )

    if pk:
        results = results.exclude(pk=pk)

    entries = results.values("source", "target", "quality").annotate(
        project_name=F("project__name")
    )
    return sort_query_results(entries)


def sort_query_results(entries):
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
    return sort_query_results(entries)
