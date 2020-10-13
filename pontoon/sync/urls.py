from django.conf.urls import url
from django.views.generic import RedirectView

from pontoon.sync import views


urlpatterns = [
    # Redirect until we use it for something more meaningful
    url(
        r"^sync/$",
        RedirectView.as_view(pattern_name="pontoon.sync.logs.list", permanent=True),
    ),
    url(r"^sync/log/$", views.sync_log_list, name="pontoon.sync.logs.list"),
    url(
        r"^sync/log/(?P<sync_log_pk>\d+)/",
        views.sync_log_details,
        name="pontoon.sync.logs.details",
    ),
]
