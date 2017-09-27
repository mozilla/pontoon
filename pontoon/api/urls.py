from csp.decorators import csp_exempt
from graphene_django.views import GraphQLView

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from pontoon.settings import DEV
from pontoon.api.schema import schema


urlpatterns = [
    # GraphQL endpoint. In DEV mode it serves the GraphiQL IDE if accessed with Accept: text/html
    url(
        r'^graphql',
        csp_exempt(csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=DEV)))
    ),
]
