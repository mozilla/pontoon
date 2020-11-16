from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Machinery Metasearch
    path("machinery/", views.machinery, name="pontoon.machinery"),
    # Legacy: Redirect to /machinery
    path(
        "search/",
        RedirectView.as_view(pattern_name="pontoon.machinery", permanent=True),
    ),
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
    path("google-translate/", views.google_translate, name="pontoon.google_translate"),
    path(
        "microsoft-translator/",
        views.microsoft_translator,
        name="pontoon.microsoft_translator",
    ),
    path(
        "systran-translate/", views.systran_translate, name="pontoon.systran_translate",
    ),
    path("caighdean/", views.caighdean, name="pontoon.caighdean"),
    path(
        "microsoft-terminology/",
        views.microsoft_terminology,
        name="pontoon.microsoft_terminology",
    ),
    path("transvision/", views.transvision, name="pontoon.transvision"),
]
