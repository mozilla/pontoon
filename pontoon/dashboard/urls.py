from django.urls import path

from pontoon.dashboard.views import dashboard, dashboard_config


urlpatterns = [
    path(
        "dashboard/",
        dashboard,
        name="pontoon.dashboard",
    ),
    path(
        "dashboard/config",
        dashboard_config,
        name="pontoon.dashboard.config",
    ),
]
