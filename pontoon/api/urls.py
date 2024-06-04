from django.urls import path

from graphene_django.views import GraphQLView

from pontoon.api.schema import schema
from pontoon.settings import DEV


urlpatterns = [
    # GraphQL endpoint. In DEV mode it serves the GraphiQL IDE if accessed with Accept: text/html
    path(
        "graphql",
        GraphQLView.as_view(schema=schema, graphiql=DEV),
    ),
]
