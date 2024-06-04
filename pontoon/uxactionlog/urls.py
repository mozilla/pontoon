from . import views
from django.urls import path


urlpatterns = [
    # AJAX: Save a new UX action in the database
    path(
        "log-ux-action/",
        views.log_ux_action,
        name="pontoon.uxactionlog.log_ux_action",
    ),
]
