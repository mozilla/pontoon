from . import views
from django.urls import path


urlpatterns = [
    # Insights page
    path(
        "insights/",
        views.insights,
        name="pontoon.insights",
    ),
]
