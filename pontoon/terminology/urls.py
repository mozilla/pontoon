from __future__ import absolute_import

from django.conf.urls import url

from . import views

urlpatterns = [
    # AJAX: Retrieve terms for given Entity and Locale
    url(r"^get-terms/", views.get_terms, name="pontoon.terms.get"),
    # AJAX: Download terminology
    url(
        r"^(?P<locale>.+)\.tbx$",
        views.download_terminology,
        name="pontoon.download_tbx",
    ),
]
