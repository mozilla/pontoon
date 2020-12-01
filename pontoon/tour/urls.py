from django.urls import path

from . import views

urlpatterns = [
    path(
        "update-tour-status/",
        views.update_tour_status,
        name="pontoon.update_tour_status",
    ),
]
