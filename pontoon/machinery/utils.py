import google.auth
import google.auth.transport.requests
import json
import Levenshtein
import logging
import operator
import os
import requests

from collections import defaultdict
from functools import reduce
from html import unescape
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import translate
from google.oauth2 import service_account

from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q

import pontoon.base as base
from pontoon.base.placeables import get_placeables

log = logging.getLogger(__name__)
MAX_RESULTS = 5


def get_google_translate_data(text, locale, format="text", preserve_placeables=False):
    res = (
        get_google_automl_translation(text, locale, format, preserve_placeables)
        if locale.google_automl_model
        else get_google_generic_translation(text, locale.google_translate_code, format)
    )
    if format == "html" and "translation" in res:
        res["translation"] = unescape(res["translation"])

    return res


def get_google_generic_translation(text, locale_code, format="text"):
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
        "format": format,
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


def get_google_automl_translation(
    text, locale, format="text", preserve_placeables=False
):
    try:
        client = translate.TranslationServiceClient()
    except DefaultCredentialsError as e:
        log.error(f"Google AutoML Translation error: {e}")
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

    # Google AutoML Translation requires location "us-central1"
    location = "us-central1"

    parent = f"projects/{project_id}/locations/{location}"
    model_id = locale.google_automl_model
    model_path = f"{parent}/models/{model_id}"

    request_params = {
        "contents": [text],
        "target_language_code": locale.google_translate_code,
        "model": model_path,
        "source_language_code": "en",
        "parent": parent,
        "mime_type": "text/html" if format == "html" else "text/plain",
    }

    if preserve_placeables:
        use_placeables_glossary(text, client, project_id, location, request_params)

    # Get translations
    response = client.translate_text(request=request_params)

    translations = response.translations
    if response.glossary_translations:
        translations = response.glossary_translations

    if len(translations) == 0:
        return {
            "status": False,
            "message": "No translations found.",
        }
    else:
        return {
            "status": True,
            "translation": translations[0].translated_text,
        }


def use_placeables_glossary(text, client, project_id, location, request_params):
    placeables = get_placeables(text)

    if not placeables:
        return

    glossary_id = "placeables"
    glossary_path = client.glossary_path(project_id, location, glossary_id)
    url = f"https://translation.googleapis.com/v3/{glossary_path}/glossaryEntries"

    auth_req = google.auth.transport.requests.Request()
    credentials = service_account.Credentials.from_service_account_file(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    credentials.refresh(auth_req)
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # Retrieve already stored glossary terms
    existing_terms = get_existing_terms(url, headers)

    # Store any new terms to the glossary
    if existing_terms:
        new_terms = {term for term in placeables if term not in existing_terms}

        if new_terms:
            store_new_terms(url, headers, new_terms)

    glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary_path)
    request_params["glossary_config"] = glossary_config


def get_existing_terms(url, headers):
    # TODO: Placeables should be cached in a new DB table, that will be updated in
    # store_new_terms() and synced daily from upstream to account for any drift.
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error(f"Retrieving existing glossary terms failed: {e}")
        return None

    return [
        term["text"]
        for termset in r.json()["glossaryEntries"]
        for term in termset["termsSet"]["terms"]
        if term["languageCode"] == "en"
    ]


def store_new_terms(url, headers, new_terms):
    locale_codes = ["en"] + sorted(
        base.models.Locale.objects.exclude(google_translate_code__in=["en", ""])
        .order_by()  # Clear default ordering on the Locale model
        .values_list("google_translate_code", flat=True)
        .distinct()
    )

    for new_term in new_terms:
        data = {
            "termsSet": {
                "terms": [
                    {
                        "languageCode": locale_code,
                        "text": new_term,
                    }
                    for locale_code in locale_codes
                ],
            }
        }

        try:
            r = requests.post(url, headers=headers, data=json.dumps(data))
            r.raise_for_status()
        except requests.exceptions.RequestException:
            log.error(f"Adding new glossary terms failed: {r.content}")


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
