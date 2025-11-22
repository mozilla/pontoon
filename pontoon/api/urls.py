from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerSplitView

from django.urls import include, path

from pontoon.api import views


api_v2_patterns = [
    path(
        # Locales
        "locales/",
        views.LocaleListView.as_view(),
        name="locale-list",
    ),
    path(
        # Locale
        "locales/<str:code>/",
        views.LocaleIndividualView.as_view(),
        name="locale-individual",
    ),
    path(
        # Projects
        "projects/",
        views.ProjectListView.as_view(),
        name="project-list",
    ),
    path(
        # Project
        "projects/<str:slug>/",
        views.ProjectIndividualView.as_view(),
        name="project-individual",
    ),
    path(
        "entities/",
        views.EntityListView.as_view(),
        name="entity-list",
    ),
    path(
        "entities/<int:pk>/",
        views.EntityIndividualView.as_view(),
        name="entity-individual",
    ),
    path(
        "entities/<slug:project>/<path:resource>/<str:entity>/",
        views.EntityIndividualView.as_view(),
        name="entity-individual-alternate",
    ),
    path(
        # Terminology Search
        "search/terminology/",
        views.TermSearchListView.as_view(),
        name="term-search",
    ),
    path(
        # Translation Memory Search
        "search/tm/",
        views.TranslationMemorySearchListView.as_view(),
        name="translation-memory-search",
    ),
    path(
        # Entity Translation Search
        "search/translations/",
        views.TranslationSearchListView.as_view(),
        name="entity-translation-search",
    ),
    path(
        # ProjectLocale
        "<str:code>/<str:slug>/",
        views.ProjectLocaleIndividualView.as_view(),
        name="project-locale-individual",
    ),
    path(
        # User Actions
        "user-actions/<str:date>/project/<slug:slug>/",
        views.UserActionsView.as_view(),
        name="user-actions",
    ),
]


urlpatterns = [
    # REST API
    path("api/v2/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v2/",
        SpectacularSwaggerSplitView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v2/", include(api_v2_patterns)),
]
