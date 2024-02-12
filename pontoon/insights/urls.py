from django.urls import path
from django.views.decorators.cache import cache_page

from pontoon.settings import VIEW_CACHE_TIMEOUT

from . import views

urlpatterns = [
    # Insights page
    path(
        "insights/",
        cache_page(VIEW_CACHE_TIMEOUT)(views.insights),
        name="pontoon.insights",
    ),
]
