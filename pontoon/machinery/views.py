import logging
import requests
import xml.etree.ElementTree as ET
from uuid import uuid4
from six.moves.urllib.parse import quote

from collections import defaultdict
from django.conf import settings
from django.db import DataError
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError

from pontoon.base import utils
from pontoon.base.models import Locale, TranslationMemoryEntry


log = logging.getLogger(__name__)


def machinery(request):
    locale = utils.get_project_locale_from_request(request, Locale.objects) or 'en-GB'

    return render(request, 'machinery/machinery.html', {
        'locale': Locale.objects.get(code=locale),
        'locales': Locale.objects.all(),
    })


def translation_memory(request):
    """Get translations from internal translations memory."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        pk = request.GET['pk']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    max_results = 5
    locale = get_object_or_404(Locale, code=locale)
    entries = (
        TranslationMemoryEntry.objects
        .minimum_levenshtein_ratio(text)
        .filter(locale=locale)
        .exclude(translation__approved=False, translation__fuzzy=False)
    )

    # Exclude existing entity
    if pk:
        entries = entries.exclude(entity__pk=pk)

    entries = entries.values('source', 'target', 'quality').order_by('-quality')
    suggestions = defaultdict(lambda: {'count': 0, 'quality': 0})

    try:
        for entry in entries:
            if (
                entry['target'] not in suggestions or
                entry['quality'] > suggestions[entry['target']]['quality']
            ):
                suggestions[entry['target']].update(entry)
            suggestions[entry['target']]['count'] += 1
    except DataError as e:
        # Catches 'argument exceeds the maximum length of 255 bytes' Error
        return HttpResponse('Not Implemented: {error}'.format(error=e), status=501)

    return JsonResponse(
        sorted(suggestions.values(), key=lambda e: e['count'], reverse=True)[:max_results],
        safe=False
    )


def machine_translation(request):
    """Get translation from machine translation service."""
    try:
        text = request.GET['text']
        locale_code = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    api_key = settings.MICROSOFT_TRANSLATOR_API_KEY

    if not api_key:
        log.error("MICROSOFT_TRANSLATOR_API_KEY not set")
        return HttpResponseBadRequest("Missing api key.")

    # Validate if locale exists in the database to avoid any potential XSS attacks.
    get_list_or_404(Locale, ms_translator_code=locale_code)

    obj = {
        'locale': locale_code,
    }
    url = "http://api.microsofttranslator.com/V2/Http.svc/Translate"
    payload = {
        "appId": api_key,
        "text": text,
        "from": "en",
        "to": locale_code,
        "contentType": "text/html",
    }
    try:
        r = requests.get(url, params=payload)
        # Parse XML response
        root = ET.fromstring(r.content)
        translation = root.text
        obj['translation'] = translation

        return JsonResponse(obj)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def microsoft_terminology(request):
    """Get translations from Microsoft Terminology Service."""
    try:
        text = request.GET['text']
        locale_code = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    # Validate if locale exists in the database to avoid any potential XSS attacks.
    get_list_or_404(Locale, ms_terminology_code=locale_code)

    obj = {}
    url = 'http://api.terminology.microsoft.com/Terminology.svc'
    headers = {
        'SOAPAction': (
            '"http://api.terminology.microsoft.com/terminology/Terminology/GetTranslations"'
        ),
        'Content-Type': 'text/xml; charset=utf-8'
    }
    payload = {
        'uuid': uuid4(),
        'text': quote(text.encode('utf-8')),
        'to': locale_code,
        'max_result': 5
    }
    template = get_template('machinery/microsoft_terminology.jinja')

    payload = template.render(payload)

    try:
        r = requests.post(url, data=payload, headers=headers)
        translations = []
        xpath = './/{http://api.terminology.microsoft.com/terminology}'
        root = ET.fromstring(r.content)
        results = root.find(xpath + 'GetTranslationsResult')

        if results is not None:
            for translation in results:
                translations.append({
                    'source': translation.find(xpath + 'OriginalText').text,
                    'target': translation.find(xpath + 'TranslatedText').text,
                    'quality': int(translation.find(xpath + 'ConfidenceLevel').text),
                })

            obj['translations'] = translations
        return JsonResponse(obj)

    except requests.exceptions.RequestException as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def transvision(request):
    """Get Mozilla translations from Transvision service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        text = quote(text.encode('utf-8'))
    except KeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    url = (
        u'https://transvision.mozfr.org/api/v1/tm/global/en-US/{locale}/{text}/'
        .format(locale=locale, text=text)
    )

    payload = {
        'max_results': 5,
        'min_quality': 70,
    }

    try:
        r = requests.get(url, params=payload)
        if 'error' in r.json():
            error = r.json()['error']
            log.error('Transvision error: {error}'.format(error))
            return HttpResponseBadRequest('Bad Request: {error}'.format(error=error))

        return JsonResponse(r.json(), safe=False)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))
