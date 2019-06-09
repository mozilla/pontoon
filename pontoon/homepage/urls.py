from __future__ import absolute_import

from django.conf.urls import url

from . import views

urlpatterns = [
    # Homepage
    url(r'^$', views.homepage, name='pontoon.homepage'),
]
