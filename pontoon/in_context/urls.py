from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # In-context demo
    path("in-context/", views.in_context, name="pontoon.in_context",),
    # Legacy: Redirect to /in-context
    path(
        "intro/",
        RedirectView.as_view(pattern_name="pontoon.in_context", permanent=True),
    ),
]
