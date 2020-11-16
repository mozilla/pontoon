from csp.decorators import csp_exempt
from graphene_django.views import GraphQLView

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from pontoon.api.schema import schema
from pontoon.settings import DEV


urlpatterns = [
    # GraphQL endpoint. In DEV mode it serves the GraphiQL IDE if accessed with Accept: text/html
    path(
        "graphql",
        csp_exempt(csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=DEV))),
    ),
]
