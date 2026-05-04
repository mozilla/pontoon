import hashlib
import json
import logging
import operator
import os

from collections import defaultdict
from functools import reduce
from html import unescape

import google.auth
import google.auth.transport.requests
import requests

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import translate
from google.oauth2 import service_account
from rapidfuzz.distance.Indel import normalized_distance

from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.db.models.functions import JSONObject

from pontoon.base.models import Locale, Project, ProjectLocale, TranslationMemoryEntry
from pontoon.base.placeables import get_placeables
from pontoon.base.utils import get_search_phrases


log = logging.getLogger(__name__)
MAX_RESULTS = 5


def get_machinery_service_cache_key(service, *parts):
    digest = hashlib.md5(":".join(str(p) for p in parts).encode()).hexdigest()
    return f"machinery_service:{service}:{digest}"


def set_machinery_service_cache_key(key, value):
    cache.set(key, value, settings.MACHINERY_SERVICE_CACHE_TIMEOUT)


def get_google_translate_data(text, locale, format="text", preserve_placeables=False):
    translation = (
        get_google_automl_translation(text, locale, format, preserve_placeables)
        if locale.google_automl_model
        else get_google_generic_translation(text, locale.google_translate_code, format)
    )
    if format == "html":
        translation = unescape(translation)

    return translation


def get_google_generic_translation(text, locale_code, format="text"):
    cache_key = get_machinery_service_cache_key(
        "google_generic", text, locale_code, format
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_key = settings.GOOGLE_TRANSLATE_API_KEY

    if not api_key:
        raise ImproperlyConfigured("GOOGLE_TRANSLATE_API_KEY not set")

    url = "https://translation.googleapis.com/language/translate/v2"

    payload = {
        "q": text,
        "source": "en",
        "target": locale_code,
        "format": format,
        "key": api_key,
    }

    r = requests.post(url, params=payload)
    r.raise_for_status()
    root = json.loads(r.content)

    if "data" not in root:
        raise ValueError(f"Google Translate error: {root}")

    translation = root["data"]["translations"][0]["translatedText"]
    set_machinery_service_cache_key(cache_key, translation)
    return translation


def get_google_automl_translation(
    text, locale, format="text", preserve_placeables=False
):
    cache_key = get_machinery_service_cache_key(
        "google_automl",
        text,
        locale.code,
        format,
        preserve_placeables,
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        client = translate.TranslationServiceClient()
    except DefaultCredentialsError as e:
        raise ImproperlyConfigured(
            f"Google AutoML credentials incorrectly configured: {e}"
        )

    project_id = settings.GOOGLE_AUTOML_PROJECT_ID

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_AUTOML_PROJECT_ID not set")

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
        raise ValueError("No translations found.")

    translation = translations[0].translated_text
    set_machinery_service_cache_key(cache_key, translation)
    return translation


def get_microsoft_translator_data(text, locale_code):
    cache_key = get_machinery_service_cache_key(
        "microsoft_translator", text, locale_code
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_key = settings.MICROSOFT_TRANSLATOR_API_KEY

    if not api_key:
        raise ImproperlyConfigured("MICROSOFT_TRANSLATOR_API_KEY not set")

    url = "https://api.cognitive.microsofttranslator.com/translate"
    headers = {"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/json"}
    payload = {
        "api-version": "3.0",
        "from": "en",
        "to": locale_code,
        "textType": "html",
    }
    body = [{"Text": text}]

    r = requests.post(url, params=payload, headers=headers, json=body)
    r.raise_for_status()
    root = json.loads(r.content)

    if "error" in root:
        raise ValueError(f"Unexpected response: {root}")

    translation = root[0]["translations"][0]["text"]
    set_machinery_service_cache_key(cache_key, translation)
    return translation


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
        Locale.objects.exclude(google_translate_code__in=["en", ""])
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


def get_concordance_search_data(user, text, locale):
    search_phrases = get_search_phrases(text)
    search_filters = (
        Q(
            Q(target__icontains_collate=(phrase, locale.db_collation))
            | Q(source__icontains=phrase),
            locale=locale,
        )
        for phrase in search_phrases
    )
    search_query = reduce(operator.and_, search_filters)

    projects = Project.objects.visible_for(user)
    pl_project_ids = ProjectLocale.objects.filter(locale=locale).values_list(
        "project_id", flat=True
    )

    search_results = (
        TranslationMemoryEntry.objects.filter(search_query, project__in=projects)
        .values("source", "target")
        .annotate(
            projects=JSONBAgg(
                JSONObject(
                    name="project__name",
                    slug="project__slug",
                ),
                distinct=True,
            ),
            entities=ArrayAgg(
                "entity",
                filter=Q(
                    entity__isnull=False,
                    project__disabled=False,
                    project__id__in=pl_project_ids,
                ),
                distinct=True,
            ),
        )
    )

    def sort_by_quality(entity):
        """Sort the results by their best Levenshtein distance from the search query"""

        def levenshtein_distance(s1, s2):
            return round((1 - normalized_distance(s1.lower(), s2.lower())) * 100)

        return (
            max(
                levenshtein_distance(text, entity["target"]),
                levenshtein_distance(text, entity["source"]),
            ),
            len(entity["projects"]),
        )

    return sorted(search_results, key=sort_by_quality, reverse=True)


def get_translation_memory_data(text, locale, pk=None):
    entries = TranslationMemoryEntry.objects.filter(
        locale=locale
    ).minimum_levenshtein_ratio(text)

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
