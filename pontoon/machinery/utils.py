import json
import Levenshtein
import logging
import operator
import requests

from collections import defaultdict
from functools import reduce
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import translate

from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q

import pontoon.base as base

log = logging.getLogger(__name__)
MAX_RESULTS = 5


def get_google_translate_data(text, locale_code):
    try:
        locale = base.models.Locale.objects.get(google_translate_code=locale_code)
    except base.models.Locale.DoesNotExist as e:
        return {
            "status": False,
            "message": f"{e}",
        }

    if locale.google_automl_model:
        return get_google_automl_translation(text, locale)

    return get_google_generic_translation(text, locale_code)


def get_google_generic_translation(text, locale_code):
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
            log.error(f"Google Translate error: {root}")
            return {
                "status": False,
                "message": f"Bad Request: {root}",
            }

        return {
            "status": True,
            "translation": root["data"]["translations"][0]["translatedText"],
        }

    except requests.exceptions.RequestException as e:
        log.error(f"Google Translate error: {e}")
        return {
            "status": False,
            "message": f"{e}",
        }


def get_google_automl_translation(text, locale):
    try:
        client = translate.TranslationServiceClient()
    except DefaultCredentialsError as e:
        log.error("Google AutoML Translation error: {e}")
        return {
            "status": False,
            "message": f"{e}",
        }

    project_id = settings.GOOGLE_AUTOML_PROJECT_ID

    if not project_id:
        log.error("GOOGLE_AUTOML_PROJECT_ID not set")
        return {
            "status": False,
            "message": "Bad Request: Missing Project ID.",
        }

    model_id = locale.google_automl_model

    # Google AutoML Translation requires location "us-central1"
    location = "us-central1"

    parent = f"projects/{project_id}/locations/{location}"
    model_path = f"{parent}/models/{model_id}"

    response = client.translate_text(
        request={
            "contents": [text],
            "target_language_code": locale.google_translate_code,
            "model": model_path,
            "source_language_code": "en",
            "parent": parent,
            "mime_type": "text/plain",
        }
    )

    if len(response.translations) == 0:
        return {
            "status": False,
            "message": "No translations found.",
        }
    else:
        return {
            "status": True,
            "translation": response.translations[0].translated_text,
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
        .values("source", "target")
        .annotate(project_names=ArrayAgg("project__name", distinct=True))
        .distinct()
    )

    def sort_by_quality(entity):
        """Sort the results by their best Levenshtein distance from the search query"""
        return (
            max(
                int(
                    round(
                        Levenshtein.ratio(text.lower(), entity["target"].lower()) * 100
                    )
                ),
                int(
                    round(
                        Levenshtein.ratio(text.lower(), entity["source"].lower()) * 100
                    )
                ),
            ),
            len(entity["project_names"]),
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
        entries_merged.values(),
        key=lambda e: (e["quality"], e["count"]),
        reverse=True,
    )[:MAX_RESULTS]
