from . import views
from django.urls import path


urlpatterns = [
    path(
        "update-tour-status/",
        views.update_tour_status,
        name="pontoon.update_tour_status",
    ),
]
