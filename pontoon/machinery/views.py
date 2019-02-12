import json
import logging
import requests
import xml.etree.ElementTree as ET
from uuid import uuid4
from six.moves.urllib.parse import quote

from collections import defaultdict

from django import http
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import escape

from pontoon.base import utils
from pontoon.base.models import Entity, Locale, Translation, TranslationMemoryEntry

# caighdean depends on nltk which tries to download files when it is imported.
# This is doomed to fail when you start Pontoon while offline. To let
# developers work offline, we add a safety net here.
try:
    from caighdean import Translator
    from caighdean.exceptions import TranslationError
except LookupError:
    if settings.DEV:
        # Only use this trick if this is a development server.
        Translator = TranslationError = None
    else:
        raise


log = logging.getLogger(__name__)


def machinery(request):
    locale = utils.get_project_locale_from_request(request, Locale.objects) or 'en-GB'

    return render(request, 'machinery/machinery.html', {
        'locale': Locale.objects.get(code=locale),
        'locales': Locale.objects.order_by('name', 'code'),
        'is_google_translate_supported': bool(settings.GOOGLE_TRANSLATE_API_KEY),
        'is_microsoft_translator_supported': bool(settings.MICROSOFT_TRANSLATOR_API_KEY),
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
        .filter(locale=locale)
        .minimum_levenshtein_ratio(text)
        .exclude(translation__approved=False, translation__fuzzy=False)
    )
    # Exclude existing entity
    if pk:
        entries = entries.exclude(entity__pk=pk)

    entries = entries.values('source', 'target', 'quality').order_by('-quality')
    suggestions = defaultdict(lambda: {'count': 0, 'quality': 0})

    for entry in entries:
        if (
            entry['target'] not in suggestions or
            entry['quality'] > suggestions[entry['target']]['quality']
        ):
            suggestions[entry['target']].update(entry)
        suggestions[entry['target']]['count'] += 1

    return JsonResponse(
        sorted(suggestions.values(), key=lambda e: e['count'], reverse=True)[:max_results],
        safe=False
    )


def microsoft_translator(request):
    """Get translation from Microsoft machine translation service."""
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

    url = "https://api.cognitive.microsofttranslator.com/translate"
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "api-version": "3.0",
        "from": "en",
        "to": locale_code,
        "textType": "html",
    }
    body = [
        {"Text": text}
    ]

    try:
        r = requests.post(url, params=payload, headers=headers, json=body)
        root = json.loads(r.content)

        if 'error' in root:
            log.error('Microsoft Translator error: {error}'.format(error=root))
            return HttpResponseBadRequest('Bad Request: {error}'.format(error=root))

        return JsonResponse({
            'translation': root[0]['translations'][0]['text'],
        })

    except requests.exceptions.RequestException as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def google_translate(request):
    """Get translation from Google machine translation service."""
    try:
        text = request.GET['text']
        locale_code = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    api_key = settings.GOOGLE_TRANSLATE_API_KEY

    if not api_key:
        log.error('GOOGLE_TRANSLATE_API_KEY not set')
        return HttpResponseBadRequest('Missing api key.')

    # Validate if locale exists in the database to avoid any potential XSS attacks.
    get_list_or_404(Locale, google_translate_code=locale_code)

    url = 'https://translation.googleapis.com/language/translate/v2'

    payload = {
        'q': text,
        'source': 'en',
        'target': locale_code,
        'format': 'text',
        'key': api_key,
    }

    try:
        r = requests.post(url, params=payload)
        root = json.loads(r.content)

        if 'data' not in root:
            log.error('Google Translate error: {error}'.format(error=root))
            return HttpResponseBadRequest('Bad Request: {error}'.format(error=root))

        return JsonResponse({
            'translation': root['data']['translations'][0]['translatedText'],
        })

    except requests.exceptions.RequestException as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def caighdean(request):
    """Get translation from Caighdean machine translation service."""
    try:
        entityid = int(request.GET['id'])
    except (MultiValueDictKeyError, ValueError) as e:
        return HttpResponseBadRequest(
            json.dumps(
                dict(error=400,
                     message='Bad Request: {error}'.format(error=e))),
            content_type='application/json')

    try:
        entity = get_object_or_404(Entity, id=entityid)
    except http.Http404 as e:
        return http.HttpResponseNotFound(
            json.dumps(dict(error=404, message=str(e))),
            content_type='application/json')

    try:
        text = entity.translation_set.get(locale__code='gd').string
    except Translation.DoesNotExist:
        return JsonResponse({})

    if Translator is None:
        # This can happen only if you start Pontoon while offline. See comments
        # around the import of caighdean.
        return http.HttpResponseServerError(
            json.dumps({
                'error': 500,
                'message': 'Caighdean is unavailable offline',
            }),
            content_type='application/json',
        )

    try:
        translation = Translator().translate(text)
        return JsonResponse({'original': text, 'translation': translation})
    except TranslationError as e:
        return http.HttpResponseServerError(
            json.dumps(dict(error=500, message=str(e))),
            content_type='application/json')


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
            log.error('Transvision error: {error}'.format(error=error))
            error = escape(error)
            return HttpResponseBadRequest('Bad Request: {error}'.format(error=error))

        return JsonResponse(r.json(), safe=False)

    except requests.exceptions.RequestException as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))
