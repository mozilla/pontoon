import json
import logging
import requests
import xml.etree.ElementTree as ET

from urllib.parse import quote

from caighdean import Translator
from caighdean.exceptions import TranslationError
from uuid import uuid4

from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import escape

from pontoon.base import utils
from pontoon.base.models import Entity, Locale, Translation
from pontoon.machinery.utils import (
    get_concordance_search_data,
    get_google_translate_data,
    get_translation_memory_data,
)


log = logging.getLogger(__name__)


def machinery(request):
    locale = utils.get_project_locale_from_request(request, Locale.objects) or "en-GB"

    return render(
        request,
        "machinery/machinery.html",
        {
            "locale": Locale.objects.get(code=locale),
            "locales": Locale.objects.all(),
            "is_google_translate_supported": bool(settings.GOOGLE_TRANSLATE_API_KEY),
            "is_microsoft_translator_supported": bool(
                settings.MICROSOFT_TRANSLATOR_API_KEY
            ),
            "is_systran_translate_supported": bool(settings.SYSTRAN_TRANSLATE_API_KEY),
        },
    )


def translation_memory(request):
    """Get translations from internal translations memory."""
    try:
        text = request.GET["text"]
        locale = request.GET["locale"]
        pk = int(request.GET["pk"])
    except (MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        return JsonResponse(
            {"status": False, "message": "Not Found: {error}".format(error=e)},
            status=404,
        )

    data = get_translation_memory_data(text, locale, pk)
    return JsonResponse(data, safe=False)


def concordance_search(request):
    """Search for translations in the internal translations memory."""
    try:
        text = request.GET["text"]
        locale = request.GET["locale"]
        page_results_limit = int(request.GET.get("limit", 100))
        page = int(request.GET.get("page", 1))
    except (MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        return JsonResponse(
            {"status": False, "message": "Not Found: {error}".format(error=e)},
            status=404,
        )

    paginator = Paginator(get_concordance_search_data(text, locale), page_results_limit)

    try:
        data = paginator.page(page)
    except EmptyPage:
        return JsonResponse({"results": [], "has_next": False})

    return JsonResponse(
        {"results": data.object_list, "has_next": data.has_next()}, safe=False
    )


def microsoft_translator(request):
    """Get translation from Microsoft machine translation service."""
    try:
        text = request.GET["text"]
        locale_code = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    api_key = settings.MICROSOFT_TRANSLATOR_API_KEY

    if not api_key:
        log.error("MICROSOFT_TRANSLATOR_API_KEY not set")
        return JsonResponse(
            {"status": False, "message": "Bad Request: Missing api key."}, status=400
        )

    # Validate if locale exists in the database to avoid any potential XSS attacks.
    if not Locale.objects.filter(ms_translator_code=locale_code).exists():
        return JsonResponse(
            {
                "status": False,
                "message": "Not Found: {error}".format(error=locale_code),
            },
            status=404,
        )

    url = "https://api.cognitive.microsofttranslator.com/translate"
    headers = {"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/json"}
    payload = {
        "api-version": "3.0",
        "from": "en",
        "to": locale_code,
        "textType": "html",
    }
    body = [{"Text": text}]

    try:
        r = requests.post(url, params=payload, headers=headers, json=body)
        root = json.loads(r.content)

        if "error" in root:
            log.error("Microsoft Translator error: {error}".format(error=root))
            return JsonResponse(
                {
                    "status": False,
                    "message": "Bad Request: {error}".format(error=root),
                },
                status=400,
            )

        return JsonResponse({"translation": root[0]["translations"][0]["text"]})

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )


def google_translate(request):
    """Get translation from Google machine translation service."""
    try:
        text = request.GET["text"]
        locale_code = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    # Validate if locale exists in the database to avoid any potential XSS attacks.
    if not Locale.objects.filter(google_translate_code=locale_code).exists():
        return JsonResponse(
            {
                "status": False,
                "message": "Not Found: {error}".format(error=locale_code),
            },
            status=404,
        )

    data = get_google_translate_data(text, locale_code)

    if not data["status"]:
        return JsonResponse(data, status=400)

    return JsonResponse(data)


def systran_translate(request):
    """Get translations from SYSTRAN machine translation service."""
    try:
        text = request.GET["text"]
        locale_code = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    api_key = settings.SYSTRAN_TRANSLATE_API_KEY

    if not api_key:
        log.error("SYSTRAN_TRANSLATE_API_KEY not set")
        return JsonResponse(
            {"status": False, "message": "Bad Request: Missing api key."}, status=400
        )

    # Validate if locale exists in the database to avoid any potential XSS attacks.
    try:
        locale = Locale.objects.filter(systran_translate_code=locale_code).first()
    except Locale.DoesNotExist:
        return JsonResponse(
            {
                "status": False,
                "message": "Not Found: {error}".format(error=locale_code),
            },
            status=404,
        )

    url = (
        "https://translationpartners-spn9.mysystran.com:8904/translation/text/translate"
    )

    payload = {
        "key": api_key,
        "input": text,
        "source": "en",
        "target": locale_code,
        "profile": locale.systran_translate_profile,
        "format": "text",
    }

    try:
        r = requests.post(url, params=payload)

        root = json.loads(r.content)

        if "error" in root:
            log.error("SYSTRAN error: {error}".format(error=root))
            return JsonResponse(
                {
                    "status": False,
                    "message": "Bad Request: {error}".format(error=root),
                },
                status=400,
            )

        return JsonResponse({"translation": root["outputs"][0]["output"]})

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )


def caighdean(request):
    """Get translation from Caighdean machine translation service."""
    try:
        entityid = int(request.GET["id"])
    except (MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    try:
        entity = Entity.objects.get(id=entityid)
    except Entity.DoesNotExist as e:
        return JsonResponse(
            {"status": False, "message": "Not Found: {error}".format(error=e)},
            status=404,
        )

    try:
        text = entity.translation_set.get(
            locale__code="gd",
            plural_form=None if entity.string_plural == "" else 0,
            approved=True,
        ).string
    except Translation.DoesNotExist:
        return JsonResponse({})

    try:
        translation = Translator().translate(text)
        return JsonResponse({"original": text, "translation": translation})
    except TranslationError as e:
        return JsonResponse(
            {"status": False, "message": "Server Error: {error}".format(error=e)},
            status=500,
        )


def microsoft_terminology(request):
    """Get translations from Microsoft Terminology Service."""
    try:
        text = request.GET["text"]
        locale_code = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    # Validate if locale exists in the database to avoid any potential XSS attacks.
    if not Locale.objects.filter(ms_terminology_code=locale_code).exists():
        return JsonResponse(
            {
                "status": False,
                "message": "Not Found: {error}".format(error=locale_code),
            },
            status=404,
        )

    obj = {}
    url = "http://api.terminology.microsoft.com/Terminology.svc"
    headers = {
        "SOAPAction": (
            '"http://api.terminology.microsoft.com/terminology/Terminology/GetTranslations"'
        ),
        "Content-Type": "text/xml; charset=utf-8",
    }
    payload = {
        "uuid": uuid4(),
        "text": quote(text.encode("utf-8")),
        "to": locale_code,
        "max_result": 5,
    }
    template = get_template("machinery/microsoft_terminology.jinja")

    payload = template.render(payload)

    try:
        r = requests.post(url, data=payload, headers=headers)
        translations = []
        xpath = ".//{http://api.terminology.microsoft.com/terminology}"
        root = ET.fromstring(r.content)
        results = root.find(xpath + "GetTranslationsResult")

        if results is not None:
            for translation in results:
                translations.append(
                    {
                        "source": translation.find(xpath + "OriginalText").text,
                        "target": translation.find(xpath + "TranslatedText").text,
                        "quality": int(
                            translation.find(xpath + "ConfidenceLevel").text
                        ),
                    }
                )

            obj["translations"] = translations
        return JsonResponse(obj)

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )


def transvision(request):
    """Get Mozilla translations from Transvision service."""
    try:
        text = request.GET["text"]
        locale = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    try:
        text = quote(text.encode("utf-8"))
    except KeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    url = u"https://transvision.mozfr.org/api/v1/tm/global/en-US/{locale}/{text}/".format(
        locale=locale, text=text
    )

    payload = {
        "max_results": 5,
        "min_quality": 70,
    }

    try:
        r = requests.get(url, params=payload)
        if "error" in r.json():
            error = r.json()["error"]
            log.error("Transvision error: {error}".format(error=error))
            error = escape(error)
            return JsonResponse(
                {
                    "status": False,
                    "message": "Bad Request: {error}".format(error=error),
                },
                status=400,
            )

        return JsonResponse(r.json(), safe=False)

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )
