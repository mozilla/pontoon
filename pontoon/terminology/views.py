from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from django.views.generic import ListView

from pontoon.base.models import Locale
from pontoon.base.utils import require_AJAX
from pontoon.terminology import utils
from pontoon.terminology.models import Term, TermTranslation


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
            "entity_id": term.entity_id,
        }
        payload.append(data)

    return JsonResponse(payload, safe=False)


@method_decorator(condition(etag_func=None), name="dispatch")
class DownloadTerminologyViewV2(ListView):
    def get_tbx_file_content(self, term_translations, locale_code):
        return utils.build_tbx_v2_file(term_translations, locale_code)

    def dispatch(self, request, locale, *args, **kwargs):
        locale = get_object_or_404(Locale, code=locale)
        term_translations = TermTranslation.objects.filter(
            locale=locale
        ).prefetch_related("term")
        content = self.get_tbx_file_content(term_translations, locale.code)

        response = StreamingHttpResponse(content, content_type="text/xml")
        response["Content-Disposition"] = 'attachment; filename="{locale}.tbx"'.format(
            locale=locale.code
        )
        return response


class DownloadTerminologyViewV3(DownloadTerminologyViewV2):
    def get_tbx_file_content(self, term_translations, locale_code):
        return utils.build_tbx_v3_file(term_translations, locale_code)
