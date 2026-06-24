from django.urls import path

from pontoon.insights.views import insights, insights_config


urlpatterns = [
    # Insights page
    path(
        "insights/",
        insights,
        name="pontoon.insights",
    ),
    # Insights config page
    path(
        "insights/config",
        insights_config,
        name="pontoon.insights.config",
    ),
]
