from django.urls import path
from django.views.generic import RedirectView

from pontoon.sync import views


urlpatterns = [
    path("sync/", views.sync_log_list, name="pontoon.sync.logs.list"),
    path("sync/errors/", views.sync_log_errors, name="pontoon.sync.logs.errors"),
    path(
        "sync/projects/<slug:project_slug>/",
        views.sync_log_project,
        name="pontoon.sync.logs.project",
    ),
    # Redirect to not break any links
    path(
        "sync/log/",
        RedirectView.as_view(pattern_name="pontoon.sync.logs.list", permanent=True),
    ),
]
