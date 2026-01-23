from django.urls import path

from pontoon.search.views import (
    entity,
    entity_alternate,
    entity_search,
    more_entities,
)


urlpatterns = [
    path(
        "search/",
        entity_search,
        name="pontoon.search",
    ),
    path("ajax/more-translations/", more_entities, name="pontoon.search.more"),
    path("entities/<int:pk>/", entity, name="pontoon.entity"),
    path(
        "entities/<slug:project>/<path:resource>/<str:entity>/",
        entity_alternate,
        name="pontoon.entity.alternate",
    ),
]
