from django.urls import path

from pontoon.dashboard.views import dashboard


urlpatterns = [
    path(
        "dashboard/",
        dashboard,
        name="pontoon.dashboard",
    )
]
