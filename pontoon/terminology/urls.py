from django.urls import path

from . import views

urlpatterns = [
    # AJAX: Retrieve terms for given Entity and Locale
    path("get-terms/", views.get_terms, name="pontoon.terms.get"),
    # AJAX: Download terminology in TBX 2.0
    path(
        "<locale:locale>.v2.tbx",
        views.DownloadTerminologyViewV2.as_view(),
        name="pontoon.terminology.download.tbx.v2",
    ),
    # AJAX: Download terminology in TBX 3.0
    path(
        "<locale:locale>.tbx",
        views.DownloadTerminologyViewV3.as_view(),
        name="pontoon.terminology.download.tbx.v3",
    ),
]
