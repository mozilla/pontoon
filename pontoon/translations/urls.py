from __future__ import absolute_import

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"^create/$", views.create_translation, name="pontoon.translations.create",),
    url(r"^delete/$", views.delete_translation, name="pontoon.translations.delete",),
]
