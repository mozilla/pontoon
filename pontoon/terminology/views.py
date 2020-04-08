from __future__ import absolute_import

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from pontoon.base.models import Locale
from pontoon.base.utils import require_AJAX
from pontoon.terminology.models import Term


@require_AJAX
def get_terms(request):
    """Retrieve terms for given source string and Locale."""
    try:
        source_string = request.GET["source_string"]
        locale_code = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    locale = get_object_or_404(Locale, code=locale_code)
    payload = []

    for term in Term.objects.for_string(source_string):
        data = {
            "text": term.text,
            "part_of_speech": term.part_of_speech,
            "definition": term.definition,
            "usage": term.usage,
            "translation": term.translation(locale),
        }
        payload.append(data)

    return JsonResponse(payload, safe=False)
