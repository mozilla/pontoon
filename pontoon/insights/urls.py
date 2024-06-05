from django.urls import path

from . import views


urlpatterns = [
    # Insights page
    path(
        "insights/",
        views.insights,
        name="pontoon.insights",
    ),
]
