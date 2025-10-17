from django.urls import path

from pontoon.search.views import entity, entity_alternate, translation_search


urlpatterns = [
    path(
        "new-search/",
        translation_search,
        name="pontoon.search",
    ),
    path("entities/<int:pk>/", entity, name="pontoon.entity"),
    path(
        "entities/<slug:project>/<path:resource>/<str:entity>/",
        entity_alternate,
        name="pontoon.entity.alternate",
    ),
]
