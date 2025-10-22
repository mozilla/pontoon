from django.urls import path
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    # Machinery Metasearch
    path("machinery/", views.machinery, name="pontoon.machinery"),
    # Legacy: Redirect to /machinery
    path(
        "terminology/",
        RedirectView.as_view(pattern_name="pontoon.machinery", permanent=True),
    ),
    # AJAX
    path(
        "translation-memory/",
        views.translation_memory,
        name="pontoon.translation_memory",
    ),
    path(
        "concordance-search/",
        views.concordance_search,
        name="pontoon.concordance_search",
    ),
    path("google-translate/", views.google_translate, name="pontoon.google_translate"),
    path("gpt-transform/", views.gpt_transform, name="pontoon.gpt_transform"),
    path(
        "microsoft-translator/",
        views.microsoft_translator,
        name="pontoon.microsoft_translator",
    ),
    path(
        "systran-translate/",
        views.systran_translate,
        name="pontoon.systran_translate",
    ),
    path("caighdean/", views.caighdean, name="pontoon.caighdean"),
    path(
        "microsoft-terminology/",
        views.microsoft_terminology,
        name="pontoon.microsoft_terminology",
    ),
]
