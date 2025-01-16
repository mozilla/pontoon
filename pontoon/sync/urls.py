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
    path("sync/errors/", views.sync_log_errors, name="pontoon.sync.logs.errors"),
    path(
        "sync/log/<slug:project_slug>/",
        views.sync_log_project,
        name="pontoon.sync.logs.project",
    ),
]
