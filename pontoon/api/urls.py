from graphene_django.views import GraphQLView

from django.urls import include, path, re_path

from pontoon.api import views
from pontoon.api.schema import schema
from pontoon.settings import DEV


urlpatterns = [
    # GraphQL endpoint. In DEV mode it serves the GraphiQL IDE if accessed with Accept: text/html.
    # Explicitly support URLs with or without trailing slash in order to support curl requests.
    re_path(
        r"^graphql/?$",
        GraphQLView.as_view(schema=schema, graphiql=DEV),
    ),
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
                            # General
                            path(
                                "<str:date>/",
                                views.get_user_actions,
                                name="pontoon.api.get_user_actions",
                            ),
                            # Project-specific
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
