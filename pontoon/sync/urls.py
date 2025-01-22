from django.urls import path
from django.views.generic import RedirectView

from pontoon.sync import views


urlpatterns = [
    path("sync/", views.sync_log_list, name="pontoon.sync.log"),
    path("sync/errors/", views.sync_log_errors, name="pontoon.sync.log.errors"),
    path(
        "sync/projects/<slug:project_slug>/",
        views.sync_log_project,
        name="pontoon.sync.log.project",
    ),
    # Redirect to not break any links
    path(
        "sync/log/",
        RedirectView.as_view(pattern_name="pontoon.sync.log", permanent=True),
    ),
]
