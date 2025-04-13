from graphene_django.views import GraphQLView

from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt

from pontoon.api import views
from pontoon.api.schema import schema


urlpatterns = [
    # GraphQL endpoint. Serves the GraphiQL IDE if accessed with Accept: text/html.
    # Explicitly support URLs with or without trailing slash in order to support curl requests.
    re_path(
        r"^graphql/?$",
        csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True)),
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
