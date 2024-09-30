from graphene_django.views import GraphQLView

from django.urls import re_path

from pontoon.api.schema import schema
from pontoon.settings import DEV


urlpatterns = [
    # GraphQL endpoint. In DEV mode it serves the GraphiQL IDE if accessed with Accept: text/html.
    # Explicitly support URLs with or without trailing slash in order to support curl requests.
    re_path(
        r"^graphql/?$",
        GraphQLView.as_view(schema=schema, graphiql=DEV),
    ),
]
