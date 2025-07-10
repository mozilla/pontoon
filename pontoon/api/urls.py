from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerSplitView
from graphene_django.views import GraphQLView

from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt

from pontoon.api import views
from pontoon.api.schema import schema


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
    # GraphQL endpoint. Serves the GraphiQL IDE if accessed with Accept: text/html.
    # Explicitly support URLs with or without trailing slash in order to support curl requests.
    re_path(
        r"^graphql/?$",
        csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True)),
    ),
    # REST API
    path("api/v2/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v2/",
        SpectacularSwaggerSplitView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v2/", include(api_v2_patterns)),
    # API v1
    path(
        "api/v1/",
        include(
            [
                path(
                    # User actions
                    "user-actions/",
                    include(
                        [
                            # In a given project
                            path(
                                "<str:date>/project/<slug:slug>/",
                                views.get_user_actions,
                                name="pontoon.api.get_user_actions.project",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
