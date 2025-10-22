from django.urls import path

from pontoon.search.views import (
    entity,
    entity_alternate,
    more_translations,
    translation_search,
)


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
    path("ajax/more-translations/", more_translations, name="pontoon.entity.more"),
]
