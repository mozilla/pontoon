import json
import logging
import xml.etree.ElementTree as ET

from urllib.parse import quote

import requests

from moz.l10n.message import message_from_json
from moz.l10n.model import SelectMessage
from sacremoses import MosesDetokenizer

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator
from django.http import JsonResponse
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST

from pontoon.base.models import Comment, Entity, Locale, Project, Translation
from pontoon.machinery.utils import (
    get_concordance_search_data,
    get_google_translate_data,
    get_microsoft_translator_data,
    get_translation_memory_data,
)
from pontoon.pretranslation.pretranslate import Pretranslation
from pontoon.terminology.models import Term

from .openai_service import OpenAIService


log = logging.getLogger(__name__)


def _pattern_count(message):
    """Number of independently-translatable patterns in a parsed message.

    A `PatternMessage` has one; a `SelectMessage` has one per variant. Used to
    tell single-pattern messages (nothing to compose) from multi-pattern ones.
    """
    if isinstance(message, SelectMessage):
        return len(message.variants)
    return 1 if message is not None else 0


def _machinery_error_response(service_name, e):
    log.error(f"{service_name} error: {e}")
    if isinstance(e, requests.exceptions.HTTPError):
        return JsonResponse(
            {"status": False, "message": f"{e}"},
            status=e.response.status_code,
        )
    if isinstance(e, requests.exceptions.RequestException):
        return JsonResponse({"status": False, "message": f"{e}"}, status=500)
    return JsonResponse({"status": False, "message": f"{e}"}, status=400)


def translation_memory(request):
    """Get translations from internal translations memory."""
    try:
        text = request.GET["text"]
        locale = Locale.objects.get(code=request.GET["locale"])
        pk = request.GET.get("pk", None)

        if pk is not None:
            pk = int(pk)

    except (Locale.DoesNotExist, MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    data = get_translation_memory_data(text, locale, pk)
    return JsonResponse(data, safe=False)


def machinery_composed(request):
    """
    Return a composed multi-value translation for a multi-pattern entity.

    Each translatable leaf — the entity's value and every property, with a
    selector message contributing one leaf per variant — is looked up in
    Translation Memory; leaves without a 100% TM match fall back to the requested
    MT service. Mirrors the Pretranslation pipeline so the Machinery panel can
    surface a directly-pasteable composed translation alongside the per-leaf
    results. Single-pattern entities have nothing to compose and yield an empty
    response.

    Query params:
        entity: Entity pk
        locale: Locale code
        service: one of `translation-memory`, `google-translate`,
            `microsoft-translator`. Defaults to `google-translate`.
            `translation-memory` disables MT fallback.
    """
    try:
        entity_pk = int(request.GET["entity"])
        locale = Locale.objects.get(code=request.GET["locale"])
        service = request.GET.get("service", "google-translate")
        entity = Entity.objects.select_related("resource").get(pk=entity_pk)
    except (
        Entity.DoesNotExist,
        Locale.DoesNotExist,
        MultiValueDictKeyError,
        ValueError,
    ) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"}, status=400
        )

    match service:
        case "translation-memory":
            # TM-only: no MT service is called (mt_supported=False).
            mt_service = None
            mt_service_name = "tm"
            mt_supported = False
        case "google-translate":
            mt_service = get_google_translate_data
            mt_service_name = service
            mt_supported = bool(locale.google_translate_code)
        case "microsoft-translator":
            mt_service = get_microsoft_translator_data
            mt_service_name = service
            mt_supported = bool(locale.ms_translator_code)
        case _:
            return JsonResponse(
                {
                    "status": False,
                    "message": f"Bad Request: unknown service `{service}`",
                },
                status=400,
            )

    # MT services call an external provider; translation-memory is anonymous-friendly.
    if mt_service is not None and not request.user.is_authenticated:
        return JsonResponse(
            {"status": False, "message": "Authentication required"}, status=403
        )

    # Only multi-pattern messages — those with multiple properties and/or
    # selector variants — have something to compose. A single-pattern message
    # composes to the same string the per-leaf machinery already returns, so
    # there is nothing extra to show.
    entity_value = message_from_json(entity.value) if entity.value else None
    entity_properties = entity.properties or {}
    pattern_count = _pattern_count(entity_value) + sum(
        _pattern_count(message_from_json(prop)) for prop in entity_properties.values()
    )
    if pattern_count < 2:
        return JsonResponse({})

    try:
        pt = Pretranslation(
            entity,
            locale,
            preserve_placeables=False,
            mt_service=mt_service,
            mt_service_name=mt_service_name,
            mt_supported=mt_supported,
            exclude_entity=True,
        )
        value, properties = pt.walk_entity()
        translation = pt.serialize(value, properties)
    except ValueError:
        # Raised when a leaf has no TM match and MT is unavailable. Compose
        # endpoint treats this as "nothing to show" rather than an error.
        return JsonResponse({})
    except Exception as e:
        return _machinery_error_response(f"Composed machinery ({service})", e)

    if not pt.services or translation == entity.string:
        return JsonResponse({})

    # Preserve insertion order while deduplicating. Map the internal `"tm"`
    # identifier to the SourceType the frontend uses for the badge.
    sources_used = list(
        dict.fromkeys("translation-memory" if s == "tm" else s for s in pt.services)
    )

    response = {
        "original": entity.string,
        "translation": translation,
        "sources": sources_used,
    }

    # When every leaf came from a 100% TM match (`pattern()` only accepts exact
    # source matches from TM), the composed string is a complete TM match — give
    # it the same quality badge regular TM matches get. Hybrid results that fall
    # back to MT for any leaf have no meaningful aggregate score.
    if set(pt.services) == {"tm"}:
        response["quality"] = 100

    return JsonResponse(response)


def concordance_search(request):
    """Search for translations in the internal translations memory."""
    try:
        text = request.GET["text"]
        locale = Locale.objects.get(code=request.GET["locale"])
        page_results_limit = int(request.GET.get("limit", 100))
        page = int(request.GET.get("page", 1))
    except (Locale.DoesNotExist, MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    paginator = Paginator(
        get_concordance_search_data(request.user, text, locale), page_results_limit
    )

    try:
        data = paginator.page(page)
    except EmptyPage:
        return JsonResponse({"results": [], "has_next": False})

    # JSONBAgg (used in get_concordance_search_data()) does not support using
    # distinct=True in combination with ordering, so we need to do one of them
    # manually - after pagination, to reduce the number of rows processed.
    project_order = {
        name: i
        for i, name in enumerate(
            list(
                Project.objects.order_by("disabled", "-priority", "name").values_list(
                    "name", flat=True
                )
            )
        )
    }

    for result in data.object_list:
        result["projects"] = sorted(
            result["projects"],
            key=lambda x: project_order.get(x["name"], float("inf")),
        )

    return JsonResponse(
        {"results": data.object_list, "has_next": data.has_next()}, safe=False
    )


@login_required(redirect_field_name="", login_url="/403")
def microsoft_translator(request):
    """Get translation from Microsoft machine translation service."""
    try:
        text = request.GET["text"]
        locale = Locale.objects.get(code=request.GET["locale"])

        if not locale.ms_translator_code:
            raise ValueError("Locale code not supported")

    except (Locale.DoesNotExist, MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    try:
        return JsonResponse(
            {"translation": get_microsoft_translator_data(text, locale)}
        )
    except Exception as e:
        return _machinery_error_response("Microsoft Translator", e)


@login_required(redirect_field_name="", login_url="/403")
def google_translate(request):
    """Get translation from Google machine translation service."""
    try:
        text = request.GET["text"]
        locale = Locale.objects.get(code=request.GET["locale"])

        if not locale.google_translate_code:
            raise ValueError("Locale code not supported")

    except (Locale.DoesNotExist, MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    try:
        return JsonResponse({"translation": get_google_translate_data(text, locale)})
    except Exception as e:
        return _machinery_error_response("Google Translate", e)


@require_POST
@login_required(redirect_field_name="", login_url="/403")
def gpt_transform(request):
    """
    Transforms and returns text using GPT based on specified characteristics
    like rephrasing or changing formality. Fetches all entity context (comments,
    terminology) from the database using the entity PK.
    """
    try:
        english_text = request.POST.get("english_text")
        translated_text = request.POST.get("translated_text")
        characteristic = request.POST.get("characteristic")
        locale_code = request.POST.get("locale")
        entity_pk = request.POST.get("entity_pk")

        locale = Locale.objects.get(code=locale_code)

        entity_key = None
        entity_comment = None
        group_comment = None
        resource_comment = None
        pinned_comments = None
        terms = None

        if entity_pk:
            entity = Entity.objects.select_related("resource", "section").get(
                pk=entity_pk
            )
            entity_key = entity.key[0] if entity.key else None
            entity_comment = entity.comment or None
            group_comment = (entity.section.comment if entity.section else None) or None
            resource_comment = entity.resource.comment or None

            pinned = [
                stripped
                for content in Comment.objects.filter(
                    entity=entity, pinned=True
                ).values_list("content", flat=True)
                if (stripped := strip_tags(content).strip())
            ]
            pinned_comments = pinned if pinned else None

            terms_list = [
                {
                    "text": term.text,
                    "part_of_speech": term.part_of_speech,
                    "translation": term.translation(locale),
                }
                for term in Term.objects.for_string(english_text)
            ]
            terms = terms_list if terms_list else None

        service = OpenAIService()
        transformed_text = service.get_translation(
            english_text,
            translated_text,
            characteristic,
            locale,
            entity_key=entity_key,
            entity_comment=entity_comment,
            group_comment=group_comment,
            resource_comment=resource_comment,
            pinned_comments=pinned_comments,
            terms=terms,
        )
        return JsonResponse({"translation": transformed_text})

    except Exception as e:
        return _machinery_error_response("GPT Transform", e)


def caighdean(request):
    """Get translation from Caighdean machine translation service."""
    try:
        entityid = int(request.GET["id"])
        entity = Entity.objects.get(id=entityid)
    except (Entity.DoesNotExist, MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    try:
        text = entity.translation_set.get(locale__code="gd", approved=True).string
    except Translation.DoesNotExist:
        return JsonResponse({})

    url = "https://cadhan.com/api/intergaelic/3.0"

    data = {
        "teacs": text,
        "foinse": "gd",
    }

    r = None
    try:
        r = requests.post(url, data=data)
        r.raise_for_status()

        root = json.loads(r.content)
        tokens = [x[1] for x in root]
        translation = (
            MosesDetokenizer().detokenize(tokens, return_str=True).replace("\\n", "\n")
        )

        return JsonResponse({"original": text, "translation": translation})

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"status": False, "message": f"{e}"},
            status=r.status_code if r is not None else 500,
        )


def microsoft_terminology(request):
    """Get translations from Microsoft Terminology Service."""
    try:
        text = request.GET["text"]
        locale_code = request.GET["locale"]

        if not locale_code:
            raise ValueError("Locale code is empty")

    except (MultiValueDictKeyError, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    obj = {}
    url = "https://api.terminology.microsoft.com/Terminology.svc"
    headers = {
        "SOAPAction": (
            '"http://api.terminology.microsoft.com/terminology/Terminology/GetTranslations"'
        ),
        "Content-Type": "text/xml; charset=utf-8",
    }
    payload = {
        "text": quote(text.encode("utf-8")),
        "to": locale_code,
        "max_result": 5,
    }
    template = get_template("machinery/microsoft_terminology.jinja")

    payload = template.render(payload)

    r = None
    try:
        r = requests.post(url, data=payload, headers=headers)
        r.raise_for_status()

        translations = []
        namespaces = {"a": "https://api.terminology.microsoft.com/terminology"}
        root = ET.fromstring(r.content)
        results = root.find(
            ".//{http://api.terminology.microsoft.com/terminology}GetTranslationsResult"
        )

        if results is not None:
            for translation in results:
                translations.append(
                    {
                        "source": translation.find("a:OriginalText", namespaces).text,
                        "target": translation.find(
                            ".//a:TranslatedText", namespaces
                        ).text,
                    }
                )

            obj["translations"] = translations
        return JsonResponse(obj)

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"status": False, "message": f"{e}"},
            status=r.status_code if r is not None else 500,
        )
