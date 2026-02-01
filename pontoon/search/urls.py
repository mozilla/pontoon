from django.urls import path

from pontoon.search.views import (
    entity,
    entity_alternate,
    search,
    search_results,
)


urlpatterns = [
    path(
        "search/",
        search,
        name="pontoon.search",
    ),
    path("ajax/more-translations/", search_results, name="pontoon.search.more"),
    path("entities/<int:pk>/", entity, name="pontoon.entity"),
    path(
        "entities/<slug:project>/<path:resource>/<str:entity>/",
        entity_alternate,
        name="pontoon.entity.alternate",
    ),
]
