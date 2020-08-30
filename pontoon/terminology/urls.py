from __future__ import absolute_import

from django.conf.urls import url

from . import views

urlpatterns = [
    # AJAX: Retrieve terms for given Entity and Locale
    url(r"^get-terms/", views.get_terms, name="pontoon.terms.get"),
    # AJAX: Download terminology in TBX 2.0
    url(
        r"^(?P<locale>.+)\.v2\.tbx$",
        views.download_terminology_tbx_v2,
        name="pontoon.terminology.download.tbx.v2",
    ),
    # AJAX: Download terminology in TBX 3.0
    url(
        r"^(?P<locale>.+)\.tbx$",
        views.download_terminology_tbx_v3,
        name="pontoon.terminology.download.tbx.v3",
    ),
]
