from django.urls import path

from . import views


urlpatterns = [
    # AJAX
    path(
        "translation-memory/",
        views.translation_memory,
        name="pontoon.translation_memory",
    ),
    path(
        "machinery-composed/",
        views.machinery_composed,
        name="pontoon.machinery_composed",
    ),
    path(
        "concordance-search/",
        views.concordance_search,
        name="pontoon.concordance_search",
    ),
    path("google-translate/", views.google_translate, name="pontoon.google_translate"),
    path(
        "openai-chatgpt/",
        views.openai_chatgpt,
        name="pontoon.openai_chatgpt",
    ),
    path(
        "microsoft-translator/",
        views.microsoft_translator,
        name="pontoon.microsoft_translator",
    ),
    path("caighdean/", views.caighdean, name="pontoon.caighdean"),
    path(
        "microsoft-terminology/",
        views.microsoft_terminology,
        name="pontoon.microsoft_terminology",
    ),
]
