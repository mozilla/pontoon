from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Machinery Metasearch
    url(r"^machinery/$", views.machinery, name="pontoon.machinery"),
    # Legacy: Redirect to /machinery
    url(
        r"^search/$",
        RedirectView.as_view(pattern_name="pontoon.machinery", permanent=True),
    ),
    url(
        r"^terminology/$",
        RedirectView.as_view(pattern_name="pontoon.machinery", permanent=True),
    ),
    # AJAX
    url(
        r"^translation-memory/$",
        views.translation_memory,
        name="pontoon.translation_memory",
    ),
    url(
        r"^google-translate/$", views.google_translate, name="pontoon.google_translate"
    ),
    url(
        r"^microsoft-translator/$",
        views.microsoft_translator,
        name="pontoon.microsoft_translator",
    ),
    url(
        r"^systran-translate/$",
        views.systran_translate,
        name="pontoon.systran_translate",
    ),
    url(r"^caighdean/$", views.caighdean, name="pontoon.caighdean"),
    url(
        r"^microsoft-terminology/$",
        views.microsoft_terminology,
        name="pontoon.microsoft_terminology",
    ),
    url(r"^transvision/$", views.transvision, name="pontoon.transvision"),
]
