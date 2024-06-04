from django.urls import path
from django.views.generic import RedirectView

from pontoon.sync import views


urlpatterns = [
    # Redirect until we use it for something more meaningful
    path(
        "sync/",
        RedirectView.as_view(pattern_name="pontoon.sync.logs.list", permanent=True),
    ),
    path("sync/log/", views.sync_log_list, name="pontoon.sync.logs.list"),
    path(
        "sync/log/<int:sync_log_pk>/",
        views.sync_log_details,
        name="pontoon.sync.logs.details",
    ),
]
